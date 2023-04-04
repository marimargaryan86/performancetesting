import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.service.data_api.routes import coordinates


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)
    return [
        integration.route("/coordinates", coordinates.Coordinates, name="Coordinates"),
    ]
