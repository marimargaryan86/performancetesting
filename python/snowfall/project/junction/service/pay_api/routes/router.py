import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.service.pay_api.routes import (
    balances,
    currencies,
    rates,
    transactions,
)


def get_routes(dependencies: lagom.Container) -> list[routing.Route]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route("/balances", balances.Balances, name="Balances"),
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
        integration.route("/rates", rates.Rates, name="Rate"),
    ]
