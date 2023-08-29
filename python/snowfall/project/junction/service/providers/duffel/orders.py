import random
from collections.abc import Sequence

import aiosmtplib
import httpx
import pydantic
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2
from snowfall.project.junction.service.providers.duffel import (
    cache,
    config,
    notifications,
)
from snowfall.project.junction.service.providers.duffel.booking import BookingHandler
from snowfall.project.junction.service.providers.duffel.client_factory import (
    DuffelClientFactory,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

_PROVIDER_NAME = "Duffel"


class OrdersSettings(config.DuffelConfig, application.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    price_change_tolerance_percent: float = 1.0
    storage_dsn: application.AnyDsn


async def orders(  # noqa: WPS217
    app: application.AsyncApplication[OrdersSettings],
) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    rate_limit_client = await app.stack.enter_async_context(
        RateLimitClient(
            app.settings.rate_limiter_grpc_host,
            app.settings.rate_limiter_service_configs["duffel"],
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
    duffel_client_factory = DuffelClientFactory(
        api_base_url=str(app.settings.api_base_url),
        api_key=app.settings.api_key,
        version=app.settings.api_version,
        http_client=http_client,
        rate_limit_client=rate_limit_client,
        resellers_map=app.settings.resellers_map,
    )

    await OrderConsumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_orders".format(app.name),
            binds=[(types.Exchange("orders"), "orders.offers")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("orders"),
        ),
        booking_handler=BookingHandler(
            duffel_client_factory=duffel_client_factory,
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
            price_change_tolerance_percent=app.settings.price_change_tolerance_percent,
            booking_storage=await app.stack.enter_async_context(
                filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
            ),
        ),
        offer_cache=cache.OfferCache(
            client=redis.Client(redis_connection, prefix=app.name),
        ),
    ).consume()


class OrderConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.PlaceOrderTask],
        producer_obj: producer.Producer,
        booking_handler: BookingHandler,
        offer_cache: cache.OfferCache,
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
