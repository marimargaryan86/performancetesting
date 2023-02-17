import contextlib
import random

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.service.providers.karhoo import cache, config, consumer
from snowfall.stdlib import service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import trackable, types
from snowfall.vendor.karhoo import client


async def offers(  # noqa: WPS210
    app: service.Application[config.OfferSettings],
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout.seconds,
            ),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )

        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        karhoo_client = client.KarhooClient(
            base_url=app.settings.api_base_url,
            api_key=app.settings.api_key,
            http_client=http_client,
        )

        trip_offer_search_consumer = consumer.TripOfferSearchConsumer(
            consumer_obj=amqp_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_searches".format(app.name),
                binds=[(types.Exchange("offers"), "offers.search.trip")],
                middleware_stack=[
                    trackable.ReportingMiddleware(
                        status_reporter=trackable.StatusReporter(
                            producer=amqp_producer.Producer(
                                connection=amqp_connection,
                                exchange=types.Exchange("karhoo"),
                            ),
                        ),
                    ).execute,
                ],
            ),
            producer_obj=amqp_producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange("offers"),
            ),
            karhoo_client=karhoo_client,
            redis=redis.Client[bytes](
                redis=redis_connection,
                prefix=app.name,
            ),
            ttl=app.settings.ttl,
            offers_cache=cache.OfferCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
        )

        await trip_offer_search_consumer.consume()
