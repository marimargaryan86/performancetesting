from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.service.pay_api.routes import (
    balances,
    currencies,
    transactions,
)
from snowfall.stdlib.integration.starlette.routes import health


def get_routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return [
        dependencies.route("/health", health.Health, name="Health"),
        dependencies.route("/balances", balances.Balances, name="Balances"),
        dependencies.route(
            "/currencies/{currencyId}",
            currencies.Currencies,
            name="Currencies",
        ),
        dependencies.route(
            "/transactions",
            transactions.Transactions,
            name="Transactions",
        ),
    ]
