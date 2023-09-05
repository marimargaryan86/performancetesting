"""Run with duffel token as first argument to update airlines.json."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import httpx

_Airports = dict[str, dict[str, Any]]

DUFFEL_TOKEN = sys.argv[1]
AIRPORTS_PATH = Path(__file__).with_name("airports.json")


async def duffel_update(airports: _Airports) -> None:  # noqa: WPS210
    """Use Duffel API to update airports in-place."""
    airport_keys = ("time_zone", "name", "longitude", "latitude", "iata_code")
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
        airports = {ap["iata_code"]: ap for ap in json.load(fi)}

    asyncio.run(duffel_update(airports))

    sorted_airports = sorted(airports.values(), key=lambda ap: ap["iata_code"])
    output = json.dumps(sorted_airports, ensure_ascii=False, indent=4, sort_keys=True)
    AIRPORTS_PATH.write_text("{0}\n".format(output))  # For linter...
