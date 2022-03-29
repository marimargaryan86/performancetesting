import random
from typing import Sequence

import aiofiles
import aioredis
from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.geodata import geocoding
from snowfall.junction.gtfs_feed import importer, places, schedules
from snowfall.stdlib import service
from snowfall.stdlib.persistence.mongo import temporary
from snowfall.stdlib.transport import amqp


class _Settings(service.Settings):
    amqp_dsn: Sequence[AnyUrl]
    feed_ref: str
    feed_url: AnyUrl
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: Sequence[AnyUrl]
    skip_checksum_check: bool = False


async def _main(app: service.Application[_Settings]) -> None:
    temp_db = temporary.TemporaryDatabase(
        motor_asyncio.AsyncIOMotorClient(
            random.choice(app.settings.mongo_dsn),  # nosec
        ),
        prefix="gtfs_feed",
    )
    redis = aioredis.from_url(
        random.choice(app.settings.redis_dsn),  # nosec
        decode_responses=True,
    )

    async with temp_db as database:
        async with redis.client() as redis_conn:
            await _import(
                app,
                redis_conn,
                importer.RepositoryCollection.create_for_database(database),
                geocoding.ReverseGeocoder(redis_conn, app.user_agent),
            )


async def _import(
    app: service.Application[_Settings],
    redis: aioredis.Redis,
    repositories: importer.RepositoryCollection,
    geocoder: geocoding.ReverseGeocoder,
) -> None:
    async with aiofiles.tempfile.TemporaryDirectory() as temp:  # type: ignore[attr-defined]
        feed_importer = importer.Importer(
            redis,
            repositories,
            temp,
            app.user_agent,
        )

        imported = await feed_importer.import_feed(
            app.settings.feed_ref,
            app.settings.feed_url,
            app.settings.skip_checksum_check,
        )

    if not imported:
        return

    async with amqp.Connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        try:
            await _process(connection, geocoder, repositories, app.settings.feed_ref)
        except Exception as err:
            await feed_importer.clear_cached_hash(app.settings.feed_ref)
            raise err


async def _process(
    connection: amqp.Connection,
    geocoder: geocoding.ReverseGeocoder,
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
        await amqp.create_producer(
            conn=connection,
            exchange_name="places",
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
