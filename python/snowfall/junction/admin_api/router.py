from lagom.integrations import starlette
from starlette import routing

from snowfall.junction.admin_api.routes import health


def get_routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return [
        dependencies.route("/health", health.Health, name="Health"),
    ]
