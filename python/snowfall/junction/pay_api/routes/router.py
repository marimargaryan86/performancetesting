from lagom.integrations import starlette
from starlette import routing

from snowfall.junction.pay_api.routes import balances, health, transactions


def get_routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return [
        dependencies.route("/health", health.Health, name="Health"),
        dependencies.route("/balances", balances.Balances, name="Balances"),
        dependencies.route(
            "/transactions",
            transactions.Transactions,
            name="Transactions",
        ),
    ]
