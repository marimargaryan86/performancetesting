from lagom.integrations import starlette
from starlette import routing

from snowfall.junction.admin_api.routes import places
from snowfall.stdlib.integration.starlette.routes import health


def get_routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return [
        dependencies.route("/health", health.Health, name="Health"),
        dependencies.route("/places", places.Places, name="Places"),
        dependencies.route("/places/{placeId}", places.Place, name="Place"),
    ]
