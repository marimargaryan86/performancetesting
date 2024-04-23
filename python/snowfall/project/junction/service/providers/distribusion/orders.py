import aiosmtplib

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2
from snowfall.project.junction.service.providers.distribusion import (
    cache,
    config,
    notifications,
)
from snowfall.project.junction.service.providers.distribusion.booking import (
    BookingHandler,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    grpc_factory,
    httpx_factory,
    redis_factory,
)
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.distribusion import client
from snowfall.vendor.rate_limiter import gubernator_pb2_grpc
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

_PROVIDER_NAME = "Distribusion"


async def orders(  # noqa: WPS217
    app: application.Application[config.OrdersSettings],
) -> None:
    http_client = await httpx_factory.make_client(app, timeout=app.settings.api_timeout)
    rate_limit_client = RateLimitClient(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["distribusion"],
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
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
        price_quote_cache=cache.PriceQuoteCache(client=redis_client),
    ).consume()


class OrderConsumer:
    def __init__(
        self,
        consumer_obj: amqp_consumer.Consumer[amqp_pb2.PlaceOrderTask],
        producer_obj: producer.Producer,
        booking_handler: BookingHandler,
        price_quote_cache: cache.PriceQuoteCache,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._booking = booking_handler
        self._price_quote_cache = price_quote_cache
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: types.Message[amqp_pb2.PlaceOrderTask],
    ) -> None:
        price_quote = await self._price_quote_cache.fetch(
            amqp_message.body.booking.trip_option.price_quote_id,
        )

        amqp_message.body.booking.provider_name = _PROVIDER_NAME

        if not price_quote:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=amqp_message.body.booking.id,
                key=amqp_message.body.booking.trip_option.id,
            )

            return

        await self._producer.publish(
            await self._booking.book(task=amqp_message.body, price_quote=price_quote),
            routing_key="orders.result.offer",
        )
