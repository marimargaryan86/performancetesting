from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.flights import (
    endpoints,
)


def no_such_route() -> None:
    """It hasn't been added yet."""


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return [
        integration.route(
            "/flights/searches",
            endpoints.FlightSearch,
            name="FlightsSearch",
        ),
        integration.route(
            "/flights/searches/{searchId:str}",
            endpoints.FlightSearchStatus,
            name="FlightsSearchStatus",
        ),
        integration.route(
            "/flights/searches/{searchId:str}/results",
            endpoints.FlightSearchRetrieval,
            name="FlightsSearchRetrieval",
        ),
        integration.route(
            "/flights/offers/{offerId:str}/passengers",
            endpoints.FlightOfferAddPassenger,
            name="FlightOfferAddPassenger",
        ),
        integration.route(
            "/flights/offers/{offerId:str}",
            endpoints.FlightOfferRetrieval,
            name="FlightOfferRetrieval",
        ),
        integration.route(
            "/passengers/{passengerId:str}",
            no_such_route,
            name="FlightPassenger",
        ),
    ]
