from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.service.admin_api.routes import locations, places
from snowfall.stdlib.integration.starlette.routes import health


def get_routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return [
        dependencies.route("/health", health.Health, name="Health"),
        dependencies.route("/locations", locations.Locations, name="Locations"),
        dependencies.route(
            "/locations/{locationId}",
            locations.Location,
            name="Location",
        ),
        dependencies.route("/places", places.Places, name="Places"),
        dependencies.route("/places/{placeId}", places.Place, name="Place"),
    ]
