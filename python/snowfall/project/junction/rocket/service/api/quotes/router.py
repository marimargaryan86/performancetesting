from lagom.integrations import starlette
from starlette import routing


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return []
