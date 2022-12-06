from snowfall.project.junction.service.providers.distribusion import (
    config,
    offers,
    orders,
    stations,
)
from snowfall.project.junction.service.providers.distribusion.search import searches
from snowfall.stdlib import service

if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="distribusion")

    entrypoint.enter_with_commands(
        service.Command(
            name="dump-stations",
            callback=stations.dump_stations,
            settings_class=stations.DumpStationsSettings,
        ),
        service.Command(
            name="offers",
            callback=offers.offers,
            settings_class=offers.OffersSettings,
        ),
        service.Command(
            name="searches",
            callback=searches.searches,
            settings_class=searches.SearchesSettings,
        ),
        service.Command(
            name="orders",
            callback=orders.orders,
            settings_class=config.OrdersSettings,
        ),
    )
