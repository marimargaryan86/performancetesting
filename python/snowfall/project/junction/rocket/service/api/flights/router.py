from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.flights import (
    endpoints,
)


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
    ]
