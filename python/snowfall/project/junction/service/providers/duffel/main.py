import uuid

from snowfall.project.junction.provider import bookings, meta, service
from snowfall.project.junction.service.providers.duffel import (
    config,
    offers,
    orders,
    pricing,
)
from snowfall.project.junction.service.providers.duffel.booking import Transformer
from snowfall.stdlib.persistence import filesystem

_PROVIDER_ID = uuid.UUID("5d18e8e1-48e3-4b7c-82b9-62bd97a92f91")
_PROVIDER_NAME = "Duffel"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=_PROVIDER_ID, name=_PROVIDER_NAME)


async def _bookings_factory(
    app: service.AsyncApplication[config.Settings],
) -> bookings.Implementation:
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(str(app.settings.storage_dsn)),
    )

    return bookings.Implementation(
        storage=storage,
        transformer=Transformer(
            provider_identifier=_PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ).raw_to_booking,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="duffel",
        settings_class=config.Settings,
        meta_factory=_meta_factory,
        offers_factory=offers.offers_factory,
        bookings_factory=_bookings_factory,
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
            settings_class=orders.OrdersSettings,
        ),
    )
