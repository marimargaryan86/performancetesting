from snowfall.project.junction.service.providers.karhoo import config, offers
from snowfall.stdlib import service

if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="karhoo")
    entrypoint.enter_with_commands(
        service.Command(
            name="offers",
            callback=offers.offers,
            settings_class=config.OfferSettings,
        ),
    )
