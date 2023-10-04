import random

import aiosmtplib
import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2
from snowfall.project.junction.service.providers.distribusion import (
    cache,
    config,
    notifications,
)
from snowfall.project.junction.service.providers.distribusion.booking import (
    BookingHandler,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.distribusion import client
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

_PROVIDER_NAME = "Distribusion"


async def orders(  # noqa: WPS217, WPS210
    app: application.Application[config.OrdersSettings],
) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    rate_limit_client = await app.stack.enter_async_context(
        RateLimitClient(
            app.settings.rate_limiter_grpc_host,
            app.settings.rate_limiter_service_configs["distribusion"],
        ),
    )
    redis_connection = await app.stack.enter_async_context(
        aioredis.from_url(
            str(random.choice(app.settings.redis_dsn)),  # noqa: S311
            decode_responses=False,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(str(app.settings.amqp_dsn)),
    )
    distribusion_client = client.DistribusionClient(
        api_base_url=str(app.settings.api_base_url),
        api_key=app.settings.api_key,
        retailer_partner_number=app.settings.retailer_partner_number,
        http_client=http_client,
        rate_limit_client=rate_limit_client,
    )
    booking_storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )
    await OrderConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_orders".format(app.name),
            binds=[(types.Exchange("orders"), "orders.offers")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("orders"),
        ),
        booking_handler=BookingHandler(
            distribusion_client=distribusion_client,
            notifier=notifications.SmtpNotifier(
                smtp_client=aiosmtplib.SMTP(
                    hostname=app.settings.smtp_dsn.host,
                    port=int(app.settings.smtp_dsn.port or 0) or None,
                    username=app.settings.smtp_dsn.username,
                    password=app.settings.smtp_dsn.password,
                    start_tls=True,
                ),
                sender=app.settings.smtp_sender,
                recipient=app.settings.smtp_recipient,
            ),
            send_customer_email=app.settings.send_customer_email,
            booking_storage=booking_storage,
        ),
        offer_cache=cache.OffersCache(
            client=redis.Client(redis_connection, prefix=app.name),
        ),
    ).consume()


class OrderConsumer(object):
    def __init__(
        self,
        consumer_obj: amqp_consumer.Consumer[amqp_pb2.PlaceOrderTask],
        producer_obj: producer.Producer,
        booking_handler: BookingHandler,
        offer_cache: cache.OffersCache,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._booking = booking_handler
        self._cache = offer_cache
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: types.Message[amqp_pb2.PlaceOrderTask],
    ) -> None:
        offer_details = await self._cache.fetch(
            amqp_message.body.booking.trip_option.price_quote_id,
        )
        amqp_message.body.booking.provider_name = _PROVIDER_NAME

        if not offer_details:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=amqp_message.body.booking.id,
                key=amqp_message.body.booking.trip_option.id,
            )

            return

        await self._producer.publish(
            await self._booking.book(task=amqp_message.body, details=offer_details),
            routing_key="orders.result.offer",
        )
