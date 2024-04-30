from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.quotes import (
    endpoints,
)


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return [
        integration.route(
            "/quotes",
            endpoints.Quotes,
            name="CreateQuotes",
        ),
        integration.route(
            "/quotes/{quoteId}",
            endpoints.Quotes,
            name="ViewQuotes",
        ),
    ]
