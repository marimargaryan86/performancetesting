from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.trains.endpoints import searches


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return [
        integration.route(
            "/trains/searches",
            searches.TrainSearch,
            name="CreateTrainsSearch",
        ),
        integration.route(
            "/trains/searches/{searchId}",
            searches.TrainSearch,
            name="ViewTrainsSearch",
        ),
        integration.route(
            "/trains/searches/{searchId}/results",
            searches.TrainSearchResults,
            name="ListTrainsSearchResults",
        ),
    ]
