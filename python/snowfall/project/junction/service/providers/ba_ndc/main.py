from snowfall.project.junction.provider import service
from snowfall.project.junction.service.providers.ba_ndc import (
    config,
    offers,
    orders,
    pricing,
)

if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="ba_ndc")

    entrypoint.enable_offers(config.OffersSettings, offers.offers_factory)
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
