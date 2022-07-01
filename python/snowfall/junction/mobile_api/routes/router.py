from lagom.integrations import starlette
from starlette import routing

from snowfall.junction.mobile_api.routes import (
    offers,
    orders,
    payments,
    places,
    trips,
    users,
)
from snowfall.stdlib.integration.starlette.routes import health


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
        dependencies.route("/offers/searches", offers.OfferSearches),
        dependencies.route(
            "/offers/searches/{offerSearchId}/offers",
            offers.OffersByOfferSearch,
        ),
        dependencies.route("/verification-code", users.OTPGenerate),
        dependencies.route("/users/sessions", users.Session),
        dependencies.route("/users", users.Users),
        dependencies.route("/users/{userId}", users.User),
        dependencies.route("/payments", payments.Payments),
        dependencies.route("/users/{userId}/orders", users.UserOrders),
        dependencies.route(
            "/trips/searches/{tripSearchId}/trips",
            trips.TripSearchesTrips,
            name="TripSearchesTrips",
        ),
        dependencies.route("/trips/searches", trips.TripSearches, name="TripSearches"),
    ]
