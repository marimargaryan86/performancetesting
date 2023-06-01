import uuid

from snowfall.project.junction.provider import meta, service
from snowfall.project.junction.service.providers.duffel import (
    config,
    offers,
    orders,
    pricing,
)

_PROVIDER_ID = uuid.UUID("5d18e8e1-48e3-4b7c-82b9-62bd97a92f91")
_PROVIDER_NAME = "Duffel"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=_PROVIDER_ID, name=_PROVIDER_NAME)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="duffel",
        settings_class=config.Settings,
        meta_factory=_meta_factory,
        offers_factory=offers.offers_factory,
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
