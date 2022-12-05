import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.service.admin_api.routes import locations, places


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route("/locations", locations.Locations, name="Locations"),
        integration.route(
            "/locations/{locationId}",
            locations.Location,
            name="Location",
        ),
        integration.route("/places", places.Places, name="Places"),
        integration.route("/places/{placeId}", places.Place, name="Place"),
    ]
