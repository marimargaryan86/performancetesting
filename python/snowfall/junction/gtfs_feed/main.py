import random
from typing import Sequence

import aioredis
from pydantic import AnyUrl, BaseSettings

from snowfall.geodata import geocoding
from snowfall.junction.gtfs_feed.places import process_places
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import amqp


class _Settings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]
    feed_url: AnyUrl
    redis_dsn: Sequence[AnyUrl]


async def _main(service: RunnableService) -> None:
    settings = _Settings()
    connection = amqp.Connection(random.choice(settings.amqp_dsn))  # nosec
    redis = aioredis.from_url(
        random.choice(settings.redis_dsn),  # nosec
        decode_responses=True,
    )

    async with connection:
        async with redis.client() as redis_conn:
            producer = await amqp.create_producer(
                conn=connection,
                exchange_name="places",
            )

            await process_places(
                geocoding.ReverseGeocoder(redis_conn, service.user_agent),
                producer,
                settings.feed_url,
                service.user_agent,
            )


if __name__ == "__main__":
    _service = make_runnable_service(
        name="gtfs-feed",
        tasks=(Task(command="import", method=_main),),
    )

    _service.run()
