from lagom.integrations import starlette
from starlette import routing


def get_routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return []
