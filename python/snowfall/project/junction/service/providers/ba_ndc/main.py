import uuid

from snowfall.project.junction.provider import meta, service
from snowfall.project.junction.service.providers.ba_ndc import (
    config,
    offers,
    orders,
    pricing,
)

_PROVIDER_ID = uuid.UUID("f1f884bf-0be6-4ce2-8414-296a775a508d")
_PROVIDER_NAME = "British Airways NDC"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=_PROVIDER_ID, name=_PROVIDER_NAME)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="ba-ndc",
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
