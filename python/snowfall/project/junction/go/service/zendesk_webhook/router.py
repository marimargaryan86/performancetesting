import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.go.service.zendesk_webhook.routes import webhook_handler


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/zendesk_webhook",
            webhook_handler.HandleEvent,
            name="HandleEvent",
            methods=["POST"],
        ),
    ]
