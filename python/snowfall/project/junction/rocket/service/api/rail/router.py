from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.rail.endpoints import searches


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return [
        integration.route(
            "/rail/searches",
            searches.RailSearch,
            name="CreateRailSearch",
        ),
        integration.route(
            "/rail/searches/{searchId}",
            searches.RailSearch,
            name="ViewRailSearch",
        ),
        integration.route(
            "/rail/searches/{searchId}/results",
            searches.RailSearchResults,
            name="ListRailSearchResults",
        ),
    ]
