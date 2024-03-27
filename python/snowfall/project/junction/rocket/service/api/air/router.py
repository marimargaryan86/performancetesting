from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.air import (
    endpoints,
)


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return [
        integration.route(
            "/air/searches",
            endpoints.AirSearch,
            name="AirSearch",
        ),
        integration.route(
            "/air/searches/{id:str}/results",
            endpoints.AirSearchRetrieval,
            name="AirSearchRetrieval",
        ),
        integration.route(
            "/air/searches/{id:str}",
            endpoints.AirSearchStatus,
            name="AirSearchStatus",
        ),
    ]
