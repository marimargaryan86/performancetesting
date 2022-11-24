import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.service.pay_api.routes import (
    authentication,
    balances,
    currencies,
    rates,
    transactions,
)


def get_routes(dependencies: lagom.Container) -> list[routing.Route]:
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
            "/balances",
            balances.Balances,
            name="Balances",
        ),
        integration.route(
            "/currencies/{currencyId}",
            currencies.Currencies,
            name="Currencies",
        ),
        integration.route(
            "/transactions",
            transactions.Transactions,
            name="Transactions",
        ),
        integration.route(
            "/rates",
            rates.Rates,
            name="Rate",
        ),
    ]
