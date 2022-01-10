import pathlib
import uuid
import zipfile
from typing import AsyncIterator

import aiofiles
import httpx
from aiocsv import AsyncDictReader
from h3.api import numpy_int as h3

from snowfall.common.v1alpha.models_pb2 import Place


async def fetch(filename: str, feed_url: str) -> None:
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "GET",
            feed_url,
            follow_redirects=True,
        ) as response:
            response.raise_for_status()

            async with aiofiles.open(filename, mode="wb") as feed_file:
                async for chunk in response.aiter_bytes():
                    await feed_file.write(chunk)


async def unzip_stops(
    zip_handle: zipfile.ZipFile,
    namespace: uuid.UUID,
    path: str,
) -> AsyncIterator[Place]:
    stops_filepath = pathlib.Path(path, "stops.txt")

    zip_handle.extract(stops_filepath.name, path=str(stops_filepath.parent))

    async with aiofiles.open(str(stops_filepath)) as stops_file:
        async for row in AsyncDictReader(stops_file):
            row = {item_k: item_v.strip() for item_k, item_v in row.items()}

            if not row["stop_lat"] or not row["stop_lon"]:
                continue

            yield Place(
                id=str(uuid.uuid5(namespace, row["stop_id"])),
                h3_index=h3.geo_to_h3(
                    lat=float(row["stop_lat"]),
                    lng=float(row["stop_lon"]),
                    resolution=9,
                ),
                name=row["stop_name"],
            )
