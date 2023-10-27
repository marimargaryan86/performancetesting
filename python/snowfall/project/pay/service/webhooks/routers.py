import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.pay.service.webhooks import payments, refunds


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/cc/payments",
            payments.Payment,
            name="CCPayments",
            methods=["POST"],
        ),
        integration.route(
            "/stripe/refunds",
            refunds.Refunds,
            name="StripeRefunds",
            methods=["POST"],
        ),
    ]
