import pathlib
import random
from typing import Sequence

import aiofiles
import aioredis
from pydantic import AnyUrl, BaseSettings

from snowfall.format.gtfs import feed
from snowfall.geodata import geocoding
from snowfall.junction.gtfs_feed import gtfs, places, schedules
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import amqp


class _Settings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]
    feed_ref: str
    feed_url: AnyUrl
    redis_dsn: Sequence[AnyUrl]


async def _main(service: RunnableService) -> None:
    settings = _Settings()
    connection = amqp.Connection(random.choice(settings.amqp_dsn))  # nosec
    redis = aioredis.from_url(
        random.choice(settings.redis_dsn),  # nosec
        decode_responses=True,
    )

    async with aiofiles.tempfile.TemporaryDirectory() as tempdir:  # type: ignore[attr-defined]
        async with connection:
            async with redis.client() as redis_conn:
                await _import(
                    service,
                    settings,
                    connection,
                    redis_conn,
                    pathlib.Path(tempdir),
                )


async def _import(
    service: RunnableService,
    settings: _Settings,
    connection: amqp.Connection,
    redis_conn: aioredis.Redis,
    tempdir: pathlib.Path,
) -> None:
    geocoder = geocoding.ReverseGeocoder(redis_conn, service.user_agent)
    generator = schedules.SchedulesGenerator(geocoder)
    gtfs_feed = feed.FeedDecorator(
        await gtfs.fetch_feed(
            tempdir,
            settings.feed_ref,
            settings.feed_url,
            service.user_agent,
        ),
    )

    await schedules.produce_schedules(connection, generator.generate(gtfs_feed))
    await places.process_places(
        geocoder,
        await amqp.create_producer(
            conn=connection,
            exchange_name="places",
        ),
        gtfs_feed.feed,
    )


if __name__ == "__main__":
    _service = make_runnable_service(
        name="gtfs-feed",
        tasks=(Task(command="import", method=_main),),
    )

    _service.run()
