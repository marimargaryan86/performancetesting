"""Run with duffel token as first argument to update airlines.json."""

import asyncio
import json
import logging
import re
import string
import sys
from pathlib import Path
from typing import Any, cast

import httpx
from lxml.html import Element  # pants: no-infer-dep
from lxml.html import fromstring as html_fromstring

_Airports = dict[str, dict[str, Any]]

AIRPORTS_PATH = Path(__file__).parent.parent / "data" / "airports.json"
DUFFEL_TOKEN = sys.argv[1]
GOOGLE_API_KEY = "AIzaSyAnIu066pbPDKN3Kto0xtKJtjIyOCmZZJI"


class NoAirportError(ValueError):
    """Failed to get details for new airport."""


def dms_to_dec(coord: str) -> float:
    """Convert coordinate formats."""
    deg, *parts, direction = re.split("[°′″]", coord)  # noqa: RUF001
    minutes = parts[0] if parts else 0
    seconds = parts[1] if len(parts) > 1 else 0
    di = -1 if direction in {"W", "S"} else 1
    return (float(deg) + float(minutes) / 60 + float(seconds) / (60 * 60)) * di


async def _wiki_new_location(
    client: httpx.AsyncClient,
    link: Element,
) -> dict[str, str | float]:
    xpath_geo = (
        "//table[contains(@class, 'infobox')]//span[contains(@class, 'geo-dms')]/span"
    )
    xpath_valid_link = "a[not(contains(@class, 'new'))]"
    timezone_url = "https://maps.googleapis.com/maps/api/timezone/json"
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"

    try:
        path = link.xpath(xpath_valid_link)[0].get("href")
    except IndexError as ex:
        raise NoAirportError() from ex

    resp = await client.get("https://en.wikipedia.org{0}".format(path))
    html = html_fromstring(resp.content)
    try:
        lat, lon = cast(list[Element], html.xpath(xpath_geo))
    except ValueError as ec:
        raise NoAirportError() from ec
    if "latitude" not in lat.classes or "longitude" not in lon.classes:
        raise RuntimeError()
    lat = dms_to_dec(lat.text_content())
    lon = dms_to_dec(lon.text_content())
    req_params: dict[str, int | str] = {
        "location": "{0},{1}".format(lat, lon),
        "timestamp": 0,
        "key": GOOGLE_API_KEY,
    }
    resp = await client.get(timezone_url, params=req_params)
    timezone = resp.json()["timeZoneId"]

    # Get country code
    req_params = {
        "latlng": "{0},{1}".format(lat, lon),
        "result_type": "country",
        "key": GOOGLE_API_KEY,
    }
    geo_resp = await client.get(geocode_url, params=req_params)
    addr = geo_resp.json()["results"][0]["address_components"]

    return {
        "iata_country_code": addr[0]["short_name"],
        "latitude": lat,
        "longitude": lon,
        "time_zone": timezone,
    }


async def _wiki_process_page(
    client: httpx.AsyncClient,
    url: str,
    airports: _Airports,
) -> None:
    xpath_row = "//table[contains(@class, 'wikitable')]/tbody/tr[not(descendant::th)]"

    resp = await client.get(url)
    html = html_fromstring(resp.content)
    for row in cast(list[Element], html.xpath(xpath_row)):
        children = row.getchildren()
        iata = children[0].text_content().strip()
        name = children[2]
        try:
            airport = airports[iata]
        except KeyError:
            # Get details for new airport.
            try:  # noqa: WPS505
                airport = await _wiki_new_location(client, name)
            except NoAirportError:
                logging.warning(
                    "Skipped: %s - %s",  # noqa: WPS323
                    iata,
                    name.text_content(),
                )
                continue

            airport["iata_code"] = iata
            airports[iata] = airport

        try:
            node = name.xpath(".//a")[0]
        except IndexError:
            node = name
        airport["name"] = node.text_content().strip()


async def wikipedia_railways(airports: _Airports) -> None:
    """Update the IATA railways from Wikipedia in-place."""
    url = "https://en.wikipedia.org/wiki/List_of_IATA-indexed_railway_stations"
    xpath_row = (
        "//ul/li[preceding::h2[*[@id='Railway_station_codes']] and following::h2]"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        html = html_fromstring(resp.content)
        for row in cast(list[Element], html.xpath(xpath_row)):
            iata = row.xpath("b")[0].text_content().strip()
            try:
                location = airports[iata]
            except KeyError:
                # Get details for new location.
                try:  # noqa: WPS505
                    location = await _wiki_new_location(client, row)
                except NoAirportError:
                    logging.warning("Skipped: %s", row.text_content())  # noqa: WPS323
                    continue
                location["iata_code"] = iata
                airports[iata] = location

            node = row.xpath(".//a")[0]
            location["name"] = node.text_content().strip()


async def wikipedia_airports(airports: _Airports) -> None:  # noqa: WPS231
    """Update the airports from Wikipedia in-place."""
    url = "https://en.wikipedia.org/wiki/List_of_airports_by_IATA_airport_code:_{0}"
    urls = (url.format(pg) for pg in string.ascii_uppercase)

    async with httpx.AsyncClient() as client:
        await asyncio.gather(*(_wiki_process_page(client, ur, airports) for ur in urls))


async def duffel_update(airports: _Airports) -> None:
    """Use Duffel API to update airports in-place."""
    airport_keys = (
        "iata_code",
        "iata_country_code",
        "latitude",
        "longitude",
        "name",
        "time_zone",
    )
    headers = {
        "Accept-Encoding": "gzip",
        "Accept": "application/json",
        "Duffel-Version": "v1",
        "Authorization": "Bearer {0}".format(DUFFEL_TOKEN),
    }
    url = "https://api.duffel.com/air/airports"
    req_params = {"limit": 200}
    after = True

    async with httpx.AsyncClient() as client:
        while after:
            resp = await client.get(url, params=req_params, headers=headers)
            airport_results = resp.json()
            for ap in airport_results["data"]:
                airports[ap["iata_code"]] = {ke: ap[ke] for ke in airport_keys}
            after = airport_results["meta"]["after"]
            req_params["after"] = after


if __name__ == "__main__":
    with AIRPORTS_PATH.open() as fi:
        airports: _Airports = {ap["iata_code"]: ap for ap in json.load(fi)}

    # Note: Order matters. Names differ between the sources, so whichever is run last
    # will be used for any conflicting names (because each update overwrites the names).
    asyncio.run(wikipedia_railways(airports))
    asyncio.run(wikipedia_airports(airports))
    asyncio.run(duffel_update(airports))

    sorted_airports = sorted(airports.values(), key=lambda ap: ap["iata_code"])
    output = json.dumps(sorted_airports, ensure_ascii=False, indent=4, sort_keys=True)
    AIRPORTS_PATH.write_text("{0}\n".format(output))  # For linter...
