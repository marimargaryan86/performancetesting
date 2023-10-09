import contextlib
from collections.abc import Awaitable, Callable

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.service.providers.benerail import (
    booking,
    cache,
    config,
)
from snowfall.project.junction.service.providers.benerail import (
    consumer as benerail_consumer,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import amqp_factory, application
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.benerail import client


def orders_factory(
    provider_id: str,
) -> Callable[[application.Application[config.OrdersSettings]], Awaitable[None]]:
    async def orders(  # noqa: WPS430
        app: application.Application[config.OrdersSettings],
    ) -> None:
        async with contextlib.AsyncExitStack() as stack:
            http_client = await stack.enter_async_context(
                httpx.AsyncClient(
                    timeout=int(app.settings.api_timeout.total_seconds()),
                    cert=config.cert_tmp_path(app.settings.cert_base64),
                ),
            )
            logging.register(http_client)
            metrics.register(http_client)
            amqp_conn = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
            redis_conn = await stack.enter_async_context(
                aioredis.from_url(
                    str(app.settings.redis_dsn),
                    decode_responses=True,
                    retry_on_error=[aioredis.ConnectionError],
                ).client(),
            )

            orders_consumer = benerail_consumer.OrdersConsumer(
                consumer_obj=consumer.Consumer(
                    connection=amqp_conn,
                    queue_name="{0}_orders".format(app.name),
                    binds=[(types.Exchange("orders"), "orders.offers")],
                ),
                producer_obj=producer.Producer(
                    connection=amqp_conn,
                    exchange=types.Exchange("orders"),
                ),
                bookings=booking.BookingHandler(
                    benerail_client=client.BenerailClient(
                        subscription_key=app.settings.subscription_key,
                        base_url=str(app.settings.api_base_url),
                        http_client=http_client,
                    ),
                    notifications_producer=producer.Producer(
                        amqp_conn,
                        types.Exchange("notifications"),
                    ),
                    booking_storage=await stack.enter_async_context(
                        filesystem.Storage.from_dsn(app.settings.storage_dsn),
                    ),
                ),
                offers_cache=cache.OffersCache(
                    client=redis.Client(redis_conn, prefix=app.name),
                ),
                provider_id=provider_id,
            )

            await orders_consumer.consume()

    return orders
