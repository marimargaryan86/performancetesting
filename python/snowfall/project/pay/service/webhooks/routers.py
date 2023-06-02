import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.pay.service.webhooks import payments


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/webhooks/payments",
            payments.Payment,
            name="Payments",
            methods=["POST"],
        ),
    ]
