from __future__ import annotations

from snowfall.project.junction.rocket.provider import (
    meta,
    service,
)
from snowfall.project.junction.rocket.provider.v1alpha import meta_pb2
from snowfall.project.junction.rocket.service.providers.benerail import config
from snowfall.project.junction.rocket.service.providers.benerail.bookings_service import (
    bookings,
    bookings_factory,
)
from snowfall.project.junction.rocket.service.providers.benerail.constant import (
    PROVIDER_ID,
    PROVIDER_NAME,
)
from snowfall.project.junction.rocket.service.providers.benerail.pricing_service import (
    pricing,
)
from snowfall.project.junction.rocket.service.providers.benerail.searches_service import (
    search_factory,
)


async def meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(
        identifier=PROVIDER_ID,
        name=PROVIDER_NAME,
        search_capabilities=meta_pb2.SearchCapabilities(rail=True),
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="junction-rocket-providers-benerail",
        settings_class=config.Settings,
        meta_factory=meta_factory,
        search_factory=search_factory,
        bookings_factory=bookings_factory,
    )

    entrypoint.enter_with_commands(
        service.Command(
            name="pricing",
            callback=pricing,
            settings_class=config.PricingSettings,
        ),
        service.Command(
            name="bookings",
            callback=bookings,
            settings_class=config.OrdersSettings,
        ),
    )
