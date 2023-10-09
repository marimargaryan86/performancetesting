import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.pay.service.pay_api.routes import (
    authentication,
    payments,
    quotations,
    rates,
    transactions,
)


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/transactions",
            transactions.Transactions,
            name="Transactions",
            methods=["POST"],
        ),
        integration.route(
            "/transactions/{transactionId}",
            transactions.Transaction,
            name="Transactions",
            methods=["GET"],
        ),
        integration.route(
            "/rates",
            rates.Rates,
            name="Rate",
        ),
        integration.route(
            "/quotes",
            quotations.Quotations,
            name="Quotation",
        ),
    ]


def get_admin_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/users/tokens",
            authentication.Authenticate,
            name="Authenticate",
            methods=["POST"],
        ),
        integration.route(
            "/users",
            authentication.CreateUser,
            name="Authenticate",
            methods=["POST"],
        ),
        integration.route(
            "/users/me",
            authentication.ChangePassword,
            name="Authenticate",
            methods=["PATCH"],
        ),
        integration.route(
            "/payments",
            payments.Payments,
            name="Payments",
            methods=["GET", "POST"],
        ),
        integration.route(
            "/payments/{paymentId}",
            payments.Payment,
            name="Payment",
        ),
    ]
