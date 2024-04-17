from google.protobuf import message

from snowfall.project.junction.provider import bookings, meta, service
from snowfall.project.junction.provider.v1 import meta_pb2
from snowfall.project.junction.service.providers.carnect import (
    booking,
    config,
    orders,
    pricing,
    simple_offers,
)
from snowfall.project.junction.service.providers.carnect.constants import PROVIDER_ID
from snowfall.project.junction.service.providers.carnect.v1 import amqp_pb2
from snowfall.stdlib.instrumentation.httpx import logging
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import httpx_factory
from snowfall.vendor.carnect import client
from snowfall.vendor.carnect import config as carnect_settings

_PROVIDER_NAME = "Carnect"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(
        identifier=PROVIDER_ID,
        name=_PROVIDER_NAME,
        booking_capabilities=meta_pb2.BookingCapabilities(
            supports_cancellation=True,
        ),
        trip_search_capabilities=meta_pb2.TripSearchCapabilities(
            supports_trip_search=False,
            supports_simple_search=True,
        ),
    )


async def _bookings_factory(
    app: service.Application[config.Settings],
) -> bookings.Implementation:
    http_client = await httpx_factory.make_client(app, timeout=app.settings.api_timeout)
    logging.register(http_client)

    carnect_config = carnect_settings.Config(
        timeout=app.settings.ttl.seconds,
        base_url=str(app.settings.api_base_url),
        export_soap_requests=True,
        username=app.settings.api_username,
        password=app.settings.api_password,
        is_test=app.settings.is_test,
    )

    carnect_client = client.CarnectClient(
        http_client=http_client,
        config=carnect_config,
    )

    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )

    cancellation_handler = booking.BookingCancellationHandler(
        carnect_client=carnect_client,
        carnect_config=carnect_config,
    )

    return bookings.Implementation(
        storage=storage,
        transformer=booking.Transformer(
            provider_identifier=PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ).raw_to_booking,
        cancellation_handler=cancellation_handler.cancel_booking,
    )


if __name__ == "__main__":
    entrypoint: service.Entrypoint[
        config.Settings,
        message.Message,
        amqp_pb2.Criteria,
    ] = service.Entrypoint(
        name="junction-providers-carnect",
        meta_factory=_meta_factory,
        simple_offers_factory=simple_offers.simple_search_app,
        bookings_factory=_bookings_factory,
        settings_class=config.Settings,
    )
    entrypoint.enter_with_commands(
        service.Command(
            name="pricing",
            callback=pricing.price_quotes,
            settings_class=config.PricingSettings,
        ),
        service.Command(
            name="orders",
            callback=orders.orders,
            settings_class=config.OrderSettings,
        ),
    )
