from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.car_rental.endpoints import (
    offers as car_rental_offer,
)
from snowfall.project.junction.rocket.service.api.car_rental.endpoints import (
    searches as car_rental_search,
)


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return [
        integration.route(
            "/car-rental/searches",
            car_rental_search.CarSearch,
            name="CreateCarRentalSearch",
        ),
        integration.route(
            "/car-rental/searches/{searchId}",
            car_rental_search.CarSearch,
            name="ViewCarRentalSearch",
        ),
        integration.route(
            "/car-rental/searches/{searchId}/results",
            car_rental_search.CarSearchResults,
            name="ListCarSearchResults",
        ),
        integration.route(
            "/car-rental/offers/{offerId}",
            car_rental_offer.Offers,
            name="ViewCarRentalOffer",
        ),
    ]
