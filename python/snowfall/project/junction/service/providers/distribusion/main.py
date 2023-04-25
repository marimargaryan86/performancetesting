from snowfall.project.junction.provider import service
from snowfall.project.junction.service.providers.distribusion import (
    config,
    offers,
    orders,
    pricing,
    stations,
)

if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="distribusion")

    entrypoint.enable_offers(offers.OffersSettings, offers.offers)
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
