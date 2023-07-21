import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.plus.service.plus_webhooks.routes import (
    flight_stats,
    whatsapp,
)


def get_routes(
    dependencies: lagom.Container,
) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)
    return [
        integration.route("/webhooks/alerts", flight_stats.Alerts, name="Alerts"),
        integration.route(
            "/webhooks/whatsapp",
            whatsapp.IncomingMessages,
            name="IncomingMessages",
        ),
    ]
