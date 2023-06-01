import uuid

from snowfall.project.junction.provider import meta, service
from snowfall.project.junction.service.providers.distribusion import (
    config,
    offers,
    orders,
    pricing,
    stations,
)

_PROVIDER_ID = uuid.UUID("30bfba87-7077-4d96-beed-c5769cdc99c7")
_PROVIDER_NAME = "Distribusion"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=_PROVIDER_ID, name=_PROVIDER_NAME)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="distribusion",
        settings_class=config.Settings,
        meta_factory=_meta_factory,
        offers_factory=offers.offers_factory,
    )

    entrypoint.enter_with_commands(
        service.Command(
            name="dump-stations",
            callback=stations.dump_stations,
            settings_class=stations.DumpStationsSettings,
        ),
        service.Command(
            name="pricing",
            callback=pricing.price_quotes,
            settings_class=config.PricingSettings,
        ),
        service.Command(
            name="orders",
            callback=orders.orders,
            settings_class=config.OrdersSettings,
        ),
    )
