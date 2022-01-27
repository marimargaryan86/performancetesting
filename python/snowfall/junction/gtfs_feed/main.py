import random
from typing import Sequence

from geopy import adapters, geocoders
from pydantic import AnyUrl, BaseSettings
from timezonefinder import timezonefinder

from snowfall.junction.gtfs_feed.places import process_places
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import amqp


class _Settings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]
    feed_url: AnyUrl


async def _main(service: RunnableService) -> None:
    settings = _Settings()
    tz_finder = timezonefinder.TimezoneFinder()
    connection = amqp.Connection(random.choice(settings.amqp_dsn))  # nosec

    async with connection:
        producer = await amqp.create_producer(
            conn=connection,
            exchange_name="places",
        )

        async with geocoders.Photon(
            adapter_factory=adapters.AioHTTPAdapter,
            user_agent=service.user_agent,
        ) as geocoder:
            await process_places(
                geocoder,
                producer,
                tz_finder,
                settings.feed_url,
                service.user_agent,
            )


if __name__ == "__main__":
    _service = make_runnable_service(
        name="gtfs-feed",
        tasks=(Task(command="import", method=_main),),
    )

    _service.run()
