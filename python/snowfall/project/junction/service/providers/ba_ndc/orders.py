import random
from collections.abc import Sequence

import aiosmtplib
import httpx
import pydantic
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.orders.v1alpha import amqp_pb2
from snowfall.project.junction.service.providers.ba_ndc import (
    ba_ndc_helpers,
    cache,
    config,
    notifications,
)
from snowfall.project.junction.service.providers.ba_ndc.booking import BookingHandler
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.ba_ndc import client


class OrdersSettings(config.BaNdcConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr


async def orders(app: service.AsyncApplication[OrdersSettings]) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    redis_connection = await app.stack.enter_async_context(
        aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # nosec
            decode_responses=False,
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(app.settings.amqp_dsn),
    )
    ba_ndc_client = client.BaNdcClient(
        api_base_url=app.settings.api_base_url,
        api_key=app.settings.api_key,
        http_client=http_client,
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
            ba_ndc_client=ba_ndc_client,
            notifier=notifications.SmtpNotifier(
                smtp_client=aiosmtplib.SMTP(
                    hostname=app.settings.smtp_dsn.host,
                    port=int(app.settings.smtp_dsn.port or 0) or None,
                    username=app.settings.smtp_dsn.user,
                    password=app.settings.smtp_dsn.password,
                    start_tls=True,
                ),
                sender=app.settings.smtp_sender,
                recipient=app.settings.smtp_recipient,
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
        self._logger = ba_ndc_helpers.get_logger(__name__)

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: types.Message[amqp_pb2.PlaceOrderTask],
    ) -> None:
        offer_details = await self._cache.fetch(
            amqp_message.body.booking.trip_option.price_quote_id,
        )

        amqp_message.body.booking.provider_name = ba_ndc_helpers.PROVIDER_NAME

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
