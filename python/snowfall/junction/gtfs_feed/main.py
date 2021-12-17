import asyncio
import os
import pathlib
import uuid
import zipfile

import aiofiles
import h3
import httpx
from aiocsv import AsyncDictReader
from pydantic import AnyUrl, BaseSettings

from snowfall.common.v1alpha.models_pb2 import Place

_NAMESPACE = uuid.UUID("5190984e-4ab7-411e-96f6-2848cc5d63e1")


class _Settings(BaseSettings):
    feed_url: AnyUrl


async def _main() -> None:
    settings = _Settings()
    namespace = uuid.uuid5(_NAMESPACE, settings.feed_url)

    async with aiofiles.tempfile.TemporaryDirectory() as tempdir:  # type: ignore[attr-defined]
        filename = os.path.join(tempdir, "feed.zip")

        await _fetch(filename, settings)

        with zipfile.ZipFile(filename) as zip_handle:
            if zip_handle.testzip():
                raise RuntimeError(
                    "{filename} is not a valid zip file".format(filename=filename),
                )

            await _unzip(zip_handle, namespace, tempdir)


async def _fetch(filename: str, settings: _Settings) -> None:
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "GET",
            settings.feed_url,
            follow_redirects=True,
        ) as response:
            response.raise_for_status()

            async with aiofiles.open(filename, mode="wb") as feed_file:
                async for chunk in response.aiter_bytes():
                    await feed_file.write(chunk)


async def _unzip(zip_handle: zipfile.ZipFile, namespace: uuid.UUID, path: str) -> None:
    stops_filepath = pathlib.Path(path, "stops.txt")

    zip_handle.extract(stops_filepath.name, path=str(stops_filepath.parent))

    async with aiofiles.open(str(stops_filepath)) as stops_file:
        async for row in AsyncDictReader(stops_file):
            row = {item_k: item_v.strip() for item_k, item_v in row.items()}

            if not row["stop_lat"] or not row["stop_lon"]:
                continue

            Place(
                id=str(uuid.uuid5(namespace, row["stop_id"])),
                h3_index=h3.geo_to_h3(
                    lat=float(row["stop_lat"]),
                    lng=float(row["stop_lon"]),
                    resolution=9,
                ),
                name=row["stop_name"],
            )


if __name__ == "__main__":
    asyncio.run(_main())
