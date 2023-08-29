from snowfall.project.junction.service.providers.karhoo import (
    config,
    offers,
    orders,
    pricing,
)
from snowfall.stdlib.service import application

if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="karhoo")
    entrypoint.enter_with_commands(
        application.Command(
            name="offers",
            callback=offers.offers,
            settings_class=config.OfferSettings,
        ),
        application.Command(
            name="pricing",
            callback=pricing.price_quotes,
            settings_class=config.OfferSettings,
        ),
        application.Command(
            name="orders",
            callback=orders.orders,
            settings_class=config.OrderSettings,
        ),
    )
