import random
from typing import Sequence

import aiofiles
import aioredis
from motor import motor_asyncio
from pydantic import AnyUrl, BaseSettings

from snowfall.geodata import geocoding
from snowfall.junction.gtfs_feed import importer, places, schedules
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.stdlib.persistence.mongo import temporary
from snowfall.stdlib.transport import amqp


class _Settings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]
    feed_ref: str
    feed_url: AnyUrl
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: Sequence[AnyUrl]
    skip_checksum_check: bool = False


async def _main(service: RunnableService) -> None:
    settings = _Settings()
    temp_db = temporary.TemporaryDatabase(
        motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn)),  # nosec
        prefix="gtfs_feed",
    )
    redis = aioredis.from_url(
        random.choice(settings.redis_dsn),  # nosec
        decode_responses=True,
    )

    async with temp_db as database:
        async with redis.client() as redis_conn:
            await _import(
                service,
                settings,
                redis_conn,
                importer.RepositoryCollection.create_for_database(database),
                geocoding.ReverseGeocoder(redis_conn, service.user_agent),
            )


async def _import(
    service: RunnableService,
    settings: _Settings,
    redis: aioredis.Redis,
    repositories: importer.RepositoryCollection,
    geocoder: geocoding.ReverseGeocoder,
) -> None:
    async with aiofiles.tempfile.TemporaryDirectory() as temp:  # type: ignore[attr-defined]
        feed_importer = importer.Importer(
            redis,
            repositories,
            temp,
            service.user_agent,
        )

        imported = await feed_importer.import_feed(
            settings.feed_ref,
            settings.feed_url,
            settings.skip_checksum_check,
        )

    if not imported:
        return

    async with amqp.Connection(random.choice(settings.amqp_dsn)) as connection:  # nosec
        try:
            await _process(connection, geocoder, repositories, settings.feed_ref)
        except Exception as err:
            await feed_importer.clear_cached_hash(settings.feed_ref)
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
    _service = make_runnable_service(
        name="gtfs-feed",
        tasks=(Task(command="import", method=_main),),
    )

    _service.run()
