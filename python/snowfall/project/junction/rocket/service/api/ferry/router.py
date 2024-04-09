from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.ferry.endpoints import searches


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return [
        integration.route(
            "/ferry/searches",
            searches.FerrySearch,
            name="CreateFerrySearch",
        ),
        integration.route(
            "/ferry/searches/{searchId}",
            searches.FerrySearch,
            name="ViewFerrySearch",
        ),
        integration.route(
            "/ferry/searches/{searchId}/results",
            searches.FerrySearchResults,
            name="ListFerrySearchResults",
        ),
    ]
