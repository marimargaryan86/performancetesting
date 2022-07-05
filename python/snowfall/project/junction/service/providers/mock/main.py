from snowfall.project.junction.service.providers.mock import offers, orders
from snowfall.stdlib import service

if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="mock")

    entrypoint.enter_with_commands(
        service.Command(
            name="offers",
            callback=offers.offers,
            settings_class=offers.OffersSettings,
        ),
        service.Command(
            name="orders",
            callback=orders.orders,
            settings_class=orders.OrdersSettings,
        ),
    )
