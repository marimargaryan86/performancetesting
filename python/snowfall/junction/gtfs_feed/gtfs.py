import pathlib
import uuid
import zipfile
from typing import AsyncIterator, Dict

import aiofiles
import geopy
import httpx
import timezonefinder
from aiocsv import AsyncDictReader
from asyncio_throttle import throttler

from snowfall.common.v1alpha.models_pb2 import Place

_THROTTLER = throttler.Throttler(rate_limit=1)


async def fetch_feed(filename: pathlib.Path, feed_url: str, user_agent: str) -> None:
    async with httpx.AsyncClient(headers={"User-Agent": user_agent}) as client:
        async with client.stream(
            "GET",
            feed_url,
            follow_redirects=True,
        ) as response:
            response.raise_for_status()

            async with aiofiles.open(str(filename), mode="wb") as feed_file:
                async for chunk in response.aiter_bytes():
                    await feed_file.write(chunk)


async def unzip_stops(
    zip_handle: zipfile.ZipFile,
    geocoder: geopy.Photon,
    tz_finder: timezonefinder.TimezoneFinder,
    namespace: uuid.UUID,
    path: pathlib.Path,
) -> AsyncIterator[Place]:
    zip_handle.extract(path.name, path=str(path.parent))

    async with aiofiles.open(str(path)) as stops_file:
        async for row in AsyncDictReader(stops_file):
            row = {item_k: item_v.strip() for item_k, item_v in row.items()}

            if not await is_valid_stop(row):
                continue

            coords = (float(row["stop_lat"]), float(row["stop_lon"]))

            async with _THROTTLER:
                yield Place(
                    id=str(uuid.uuid5(namespace, row["stop_id"])),
                    name=row["stop_name"],
                    latitude=coords[0],
                    longitude=coords[1],
                    country_code=(
                        await geocoder.reverse(
                            "{0}, {1}".format(coords[0], coords[1]),
                            exactly_one=True,
                        )
                    ).raw["properties"]["countrycode"],
                    time_zone=tz_finder.timezone_at(lat=coords[0], lng=coords[1]),
                )


async def is_valid_stop(stop: Dict[str, str]) -> bool:
    if not stop["stop_lat"] or not stop["stop_lon"]:
        return False

    return not stop.get("parent_station")
