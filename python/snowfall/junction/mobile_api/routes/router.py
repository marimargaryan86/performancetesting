from lagom.integrations import starlette
from starlette import routing

from snowfall.junction.mobile_api.routes import health, orders, places, users


def get_routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return [
        dependencies.route("/health", health.Health, name="Health"),
        dependencies.route("/places", places.Places, name="Places"),
        dependencies.route("/orders", orders.Orders, name="ListOrders"),
        dependencies.route(
            "/orders/{orderId}",
            orders.Order,
            name="ViewOrder",
        ),
        dependencies.route("/verification-code", users.OTPGenerate),
        dependencies.route("/users", users.User),
    ]
