import aiosmtplib

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2
from snowfall.project.junction.service.providers.carnect import (
    booking,
    cache,
    config,
    constants,
    notifications,
)
from snowfall.stdlib.instrumentation.httpx import logging
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    httpx_factory,
    redis_factory,
)
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.carnect import client
from snowfall.vendor.carnect import config as carnect_settings

_PROVIDER_NAME = "Carnect"


async def orders(
    app: application.Application[config.OrderSettings],
) -> None:
    http_client = await httpx_factory.make_client(app, timeout=app.settings.api_timeout)
    logging.register(http_client)
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )

    carnect_config = carnect_settings.Config(
        timeout=app.settings.ttl.seconds,
        base_url=str(app.settings.api_base_url),
        export_soap_requests=False,
        username=app.settings.api_username,
        password=app.settings.api_password,
        is_test=app.settings.is_test,
    )

    carnect_client = client.CarnectClient(
        http_client=http_client,
        config=carnect_config,
    )

    email_client = notifications.EmailClient(
        client=aiosmtplib.SMTP(
            hostname=app.settings.smtp_dsn.host,
            port=int(app.settings.smtp_dsn.port or 0) or None,
            username=app.settings.smtp_dsn.username,
            password=app.settings.smtp_dsn.password,
            start_tls=True,
        ),
        sender=app.settings.smtp_sender,
    )

    await OrderConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_orders".format(app.name),
            binds=[(types.Exchange("orders"), "orders.offers")],
        ),
        producer_obj=amqp_producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("orders"),
        ),
        booking_handler=booking.BookingHandler(
            carnect_config=carnect_config,
            carnect_client=carnect_client,
            booking_storage=await app.stack.enter_async_context(
                filesystem.Storage.from_dsn(app.settings.storage_dsn),
            ),
            email_client=email_client,
        ),
        price_quote_cache=cache.PricingCache(
            client=redis_client,
        ),
    ).consume()


class OrderConsumer(object):
    def __init__(
        self,
        consumer_obj: amqp_consumer.Consumer[amqp_pb2.PlaceOrderTask],
        producer_obj: amqp_producer.Producer,
        booking_handler: booking.BookingHandler,
        price_quote_cache: cache.PricingCache,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._booking = booking_handler
        self._cache = price_quote_cache
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: types.Message[amqp_pb2.PlaceOrderTask],
    ) -> None:
        price_quote = await self._cache.fetch(
            amqp_message.body.booking.trip_option.price_quote_id,
        )
        amqp_message.body.booking.provider_name = _PROVIDER_NAME
        amqp_message.body.booking.provider_id = str(constants.PROVIDER_ID)

        if not price_quote:
            self._logger.warning(
                "No price quote found for booking",
                booking_id=amqp_message.body.booking.id,
                key=amqp_message.body.booking.trip_option.id,
            )

            return

        await self._producer.publish(
            await self._booking.book(task=amqp_message.body, price_quote=price_quote),
            routing_key="orders.result.offer",
        )
