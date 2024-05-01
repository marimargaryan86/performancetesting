import contextlib

import httpx

from snowfall.project.junction.rocket.provider import (
    bookings as provider_bookings,
)
from snowfall.project.junction.rocket.provider import (
    service,
)
from snowfall.project.junction.rocket.service.providers.benerail import (
    bookings as benerail_bookings,
)
from snowfall.project.junction.rocket.service.providers.benerail import (
    cache,
    helper_functions,
)
from snowfall.project.junction.rocket.service.providers.benerail.config import (
    OrdersSettings,
    Settings,
)
from snowfall.project.junction.rocket.service.providers.benerail.constant import (
    PROVIDER_ID,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import amqp_factory, redis_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.benerail import client


async def bookings(app: service.Application[OrdersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                cert=helper_functions.cert_tmp_path(app.settings.cert_base64),
            ),
        )
        logging.register(http_client)
        metrics.register(http_client)
        amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
        redis_client = await redis_factory.make_client(
            app=app,
            dsn=app.settings.redis_dsn,
            decode_responses=False,
        )

        orders_consumer = benerail_bookings.OrdersConsumer(
            consumer_obj=consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_bookings".format(app.name),
                binds=[(types.Exchange("bookings"), "bookings.prices")],
            ),
            producer_obj=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange("bookings"),
            ),
            booking_creation_handler=benerail_bookings.BookingCreationHandler(
                benerail_client_connector=client.BenerailClient(
                    subscription_key=app.settings.subscription_key,
                    base_url=str(app.settings.api_base_url),
                    http_client=http_client,
                ),
                notifications_producer=producer.Producer(
                    amqp_connection,
                    types.Exchange("notifications"),
                ),
                booking_storage=await stack.enter_async_context(
                    filesystem.Storage.from_dsn(app.settings.storage_dsn),
                ),
                use_mobile_tickets=app.settings.use_mobile_tickets,
            ),
            quote_cache=cache.BookingOffersCache(
                client=redis_client,
            ),
            provider_id=str(PROVIDER_ID),
        )

        await orders_consumer.consume()


async def bookings_factory(
    app: service.Application[Settings],
) -> provider_bookings.Implementation:
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )
    raw_to_booking = benerail_bookings.Transformer().raw_to_booking

    return provider_bookings.Implementation(
        storage=storage,
        transformer=raw_to_booking,
        cancellation_handler=benerail_bookings.CancellationHandler(
            booking_storage=storage,
            transformer=raw_to_booking,
        ).cancel,
    )
