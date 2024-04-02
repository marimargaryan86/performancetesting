from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.hotel import (
    endpoints,
)


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return [
        integration.route(
            "/hotel/searches",
            endpoints.HotelSearch,
            name="HotelSearch",
        ),
        integration.route(
            "/hotel/searches/{id:str}/results",
            endpoints.HotelSearchRetrieval,
            name="HotelSearchRetrieval",
        ),
        integration.route(
            "/hotel/searches/{id:str}",
            endpoints.HotelSearchStatus,
            name="HotelSearchStatus",
        ),
    ]
