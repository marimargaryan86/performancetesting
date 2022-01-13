import asyncio
import os
import random
import uuid
import zipfile
from typing import Sequence

import aiofiles
import aiormq
from pydantic import AnyUrl, BaseSettings
from yarl import URL

from snowfall.junction.gtfs_feed.gtfs import fetch, unzip_stops
from snowfall.transport.amqp import Producer, create_producer

_NAMESPACE = uuid.UUID("5190984e-4ab7-411e-96f6-2848cc5d63e1")


class _Settings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]
    feed_url: AnyUrl


async def _main() -> None:
    settings = _Settings()
    producer = await create_producer(
        connection=await aiormq.connect(URL(random.choice(settings.amqp_dsn))),  # nosec
        exchange_name="places",
    )
    namespace = uuid.uuid5(_NAMESPACE, settings.feed_url)

    async with aiofiles.tempfile.TemporaryDirectory() as tempdir:  # type: ignore[attr-defined]
        filename = os.path.join(tempdir, "feed.zip")

        await fetch(filename, settings.feed_url)
        await _process_places(producer, filename, namespace, tempdir)


async def _process_places(
    producer: Producer,
    filename: str,
    namespace: uuid.UUID,
    tempdir: str,
) -> None:
    with zipfile.ZipFile(filename) as zip_handle:
        if zip_handle.testzip():
            raise RuntimeError(
                "{filename} is not a valid zip file".format(filename=filename),
            )

        async for place in unzip_stops(zip_handle, namespace, tempdir):
            await producer.publish(place, "place.import")


if __name__ == "__main__":
    asyncio.run(_main())
