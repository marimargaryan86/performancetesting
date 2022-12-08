from snowfall.project.junction.service.providers.duffel import config, offers, orders
from snowfall.project.junction.service.providers.duffel.search import searches
from snowfall.stdlib import service

if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="distribusion")

    entrypoint.enter_with_commands(
        service.Command(
            name="offers",
            callback=offers.offers,
            settings_class=offers.OffersSettings,
        ),
        service.Command(
            name="searches",
            callback=searches.searches,
            settings_class=config.SearchesSettings,
        ),
        service.Command(
            name="orders",
            callback=orders.orders,
            settings_class=orders.OrdersSettings,
        ),
    )
