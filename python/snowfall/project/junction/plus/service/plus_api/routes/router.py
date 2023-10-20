import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.plus.service.plus_api.routes import (
    notification_tokens,
)


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/push-notification-tokens",
            notification_tokens.Tokens,
            methods=["PATCH"],
        ),
    ]
