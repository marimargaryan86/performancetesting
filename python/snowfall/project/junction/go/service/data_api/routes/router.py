import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.go.service.data_api.routes import locations


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)
    return [
        integration.route("/locations", locations.Locations, name="Locations"),
    ]
