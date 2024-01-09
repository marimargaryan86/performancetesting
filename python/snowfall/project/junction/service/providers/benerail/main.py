import contextlib
import os
from typing import cast

import aiosmtplib
import httpx
from aio_pika import abc

from snowfall.project.junction.provider import bookings, meta, notifications, service
from snowfall.project.junction.provider.v1 import meta_pb2
from snowfall.project.junction.service.providers.benerail import (
    booking,
    config,
    consumer,
    offers,
    orders,
    pricing,
    simple_offers,
    stations,
)
from snowfall.project.junction.service.providers.benerail.constant import PROVIDER_ID
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import amqp_factory
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.benerail import client
from snowfall.vendor.zendesk.client import ZendeskClient

_PROVIDER_NAME = "Benerail"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(
        identifier=PROVIDER_ID,
        name=_PROVIDER_NAME,
        booking_capabilities=meta_pb2.BookingCapabilities(
            supports_cancellation=True,
        ),
    )


async def _bookings_factory(
    app: service.Application[config.Settings],
) -> bookings.Implementation:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout.total_seconds(),
            cert=config.cert_tmp_path(app.settings.cert_base64),
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    benerail_client = client.BenerailClient(
        subscription_key=app.settings.subscription_key,
        base_url=str(app.settings.api_base_url),
        http_client=http_client,
    )

    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )
    cancellation_handler = booking.BookingCancellationHandler(
        benerail_client=benerail_client,
    )

    return bookings.Implementation(
        storage=storage,
        transformer=booking.Transformer(
            provider_identifier=PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ).raw_to_booking,
        cancellation_handler=cancellation_handler.cancel_booking,
    )


async def _notifications(  # noqa: WPS217
    app: service.Application[config.NotificationsSettings],
) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout.total_seconds(),
            cert=config.cert_tmp_path(app.settings.cert_base64),
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    notifier = notifications.SmtpNotifier(
        smtp_client=aiosmtplib.SMTP(
            hostname=app.settings.smtp_dsn.host,
            port=int(app.settings.smtp_dsn.port or 0) or None,
            username=app.settings.smtp_dsn.username,
            password=app.settings.smtp_dsn.password,
            start_tls=True,
        ),
        sender=app.settings.smtp_sender,
        recipient=app.settings.smtp_recipient,
    )
    benerail_client = client.BenerailClient(
        subscription_key=app.settings.subscription_key,
        base_url=str(app.settings.api_base_url),
        http_client=http_client,
    )
    zendesk_client = ZendeskClient(
        base_url=str(app.settings.zendesk_base_url),
        api_key=app.settings.zendesk_api_key,
        http_client=http_client,
        env=app.environment,
    )

    booking_storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )
    await _consume_notifications(
        app,
        amqp_connection,
        benerail_client,
        zendesk_client,
        notifier,
        booking_storage,
    )


async def _consume_notifications(
    app: service.Application[config.NotificationsSettings],
    amqp_connection: abc.AbstractConnection,
    benerail_client: client.BenerailClient,
    zendesk_client: ZendeskClient,
    notifier: notifications.SmtpNotifier,
    booking_storage: filesystem.Storage,
) -> None:
    notifications_consumer = consumer.NotificationsConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_notifications".format(app.name),
            queue_arguments={
                "x-dead-letter-exchange": "notifications.retry",
                "x-dead-letter-routing-key": "{0}.notifications.retry".format(app.name),
            },
            binds=[
                (types.Exchange("notifications"), "{0}.notifications".format(app.name)),
            ],
        ),
        benerail_client=benerail_client,
        zendesk_client=zendesk_client,
        zendesk_booked_ticket_group_id=app.settings.zendesk_booked_ticket_group_id,
        notifier=notifier,
        booking_storage=booking_storage,
    )
    await _configure_queue(app, amqp_connection)
    await notifications_consumer.consume()


async def _configure_queue(
    app: service.Application[config.NotificationsSettings],
    amqp_connection: abc.AbstractConnection,
) -> None:
    channel = await app.stack.enter_async_context(
        cast(
            contextlib.AbstractAsyncContextManager[abc.AbstractChannel],
            amqp_connection.channel(),
        ),
    )
    await channel.set_qos(
        prefetch_count=((os.cpu_count() or 1) * 2) + 1,
    )
    queue = await channel.declare_queue(
        name="{0}.notifications.retry".format(app.name),
        durable=True,
        arguments={
            "x-message-ttl": 300000,
            "x-dead-letter-exchange": "notifications",
            "x-dead-letter-routing-key": "{0}.notifications".format(app.name),
        },
    )
    exchange = types.Exchange("notifications.retry")
    declared_exchange = await channel.declare_exchange(
        name=exchange.name,
        type=exchange.type_,
        durable=True,
    )
    await queue.bind(declared_exchange, "{0}.notifications.retry".format(app.name))


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="benerail",
        offers_factory=offers.offers_app,
        simple_offers_factory=simple_offers.simple_search_app,
        meta_factory=_meta_factory,
        bookings_factory=_bookings_factory,
        settings_class=config.Settings,
    )
    entrypoint.enter_with_commands(
        service.Command(
            name="dump-stations",
            callback=stations.dump_stations,
            settings_class=config.DumpStationsSettings,
        ),
        service.Command(
            name="pricing",
            callback=pricing.price_quotes,
            settings_class=config.PriceQuoteSettings,
        ),
        service.Command(
            name="orders",
            callback=orders.orders_factory(str(PROVIDER_ID)),
            settings_class=config.OrdersSettings,
        ),
        service.Command(
            name="notifications",
            callback=_notifications,
            settings_class=config.NotificationsSettings,
        ),
    )
