import pathlib
import random
import shutil
from typing import Sequence

import aioredis
from aio_pika import abc
from aiofiles import os, tempfile  # type: ignore[attr-defined]
from motor import motor_asyncio
from pydantic import AnyUrl, DirectoryPath

from snowfall.junction.gtfs_feed import importer, places, schedules
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.logging.stdout import context_binding
from snowfall.stdlib.persistence.mongo import temporary
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.transport.grpc.client import create_channel


class _Settings(service.Settings):
    amqp_dsn: Sequence[AnyUrl]
    feeds_dir: DirectoryPath
    geodata_address: Sequence[str]
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: Sequence[AnyUrl]
    skip_checksum_check: bool = False


async def _main(app: service.Application[_Settings]) -> None:
    redis = aioredis.from_url(
        random.choice(app.settings.redis_dsn),  # nosec
        decode_responses=True,
    )

    async with redis.client() as redis_conn:
        for feed_file in app.settings.feeds_dir.glob("*.zip"):
            temp_db = temporary.TemporaryDatabase(
                motor_asyncio.AsyncIOMotorClient(
                    random.choice(app.settings.mongo_dsn),  # nosec
                ),
                prefix="gtfs_feed",
            )

            async with temp_db as database:
                await _import(
                    app,
                    feed_file,
                    redis_conn,
                    importer.RepositoryCollection.create_for_database(database),
                    geocoding_pb2_grpc.GeocodingServiceStub(
                        create_channel(
                            random.choice(app.settings.geodata_address),  # nosec
                        ),
                    ),
                )


async def _import(  # noqa: WPS210
    app: service.Application[_Settings],
    feed_file: pathlib.Path,
    redis: aioredis.Redis,
    repositories: importer.RepositoryCollection,
    geocoder: geocoding_pb2_grpc.GeocodingServiceStub,
) -> None:
    async with tempfile.TemporaryDirectory() as temp:
        new_path = pathlib.Path(temp).joinpath(feed_file.name)
        feed_ref = new_path.with_suffix("").name

        with context_binding(feed_ref=feed_ref):
            move = os.wrap(shutil.move)  # type: ignore[attr-defined]

            await move(str(feed_file), str(new_path))

            feed_importer = importer.Importer(
                redis,
                repositories,
                temp,
            )

            async with feed_importer.cache_hash(
                new_path,
                feed_ref,
            ) as checksum_matches:
                if checksum_matches and not app.settings.skip_checksum_check:
                    return

                imported = await feed_importer.import_feed(new_path)

                if not imported:
                    return

                async with await amqp.create_connection(
                    random.choice(app.settings.amqp_dsn),  # nosec
                ) as connection:
                    await _process(connection, geocoder, repositories, feed_ref)


async def _process(
    connection: abc.AbstractConnection,
    geocoder: geocoding_pb2_grpc.GeocodingServiceStub,
    repositories: importer.RepositoryCollection,
    feed_ref: str,
) -> None:
    generator = schedules.SchedulesGenerator(
        geocoder,
        feed_ref,
        repositories,
    )

    await schedules.produce_schedules(connection, generator)
    await places.process_places(
        geocoder,
        amqp.Producer(
            connection=connection,
            exchange=amqp.Exchange("places"),
        ),
        repositories,
        feed_ref,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="gtfs-feed")

    entrypoint.enter_with_commands(
        service.Command(
            name="import",
            callback=_main,
            settings_class=_Settings,
        ),
    )
