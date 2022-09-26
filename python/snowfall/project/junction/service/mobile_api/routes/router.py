from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.service.mobile_api.routes import (
    loyalty_programs,
    offers,
    orders,
    payments,
    places,
    preferences,
    trips,
    users,
)


def get_routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return [
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
        dependencies.route("/verification-code/{userEmail}", users.OTPVerify),
        dependencies.route("/users/sessions", users.Session),
        dependencies.route("/users", users.Users),
        dependencies.route("/users/me", users.UserLoggedIn),
        dependencies.route("/users/{userId}", users.User),
        dependencies.route("/users/me/preferences", preferences.Preferences),
        dependencies.route("/payments", payments.Payments),
        dependencies.route("/users/{userId}/orders", users.UserOrders),
        dependencies.route(
            "/trips/searches/{tripSearchId}/trips",
            trips.TripSearchesTrips,
            name="TripSearchesTrips",
        ),
        dependencies.route("/trips/searches", trips.TripSearches, name="TripSearches"),
        dependencies.route(
            "/loyalty-programs",
            loyalty_programs.Programs,
            name="ListLoyaltyPrograms",
        ),
    ]
