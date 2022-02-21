from lagom.integrations import starlette
from starlette import routing

from snowfall.junction.client_api.routes import health, offers, places, trips


def get_routes(dependencies: starlette.StarletteIntegration) -> list[routing.Route]:
    return [
        dependencies.route("/health", health.Health),
        dependencies.route(
            "/places",
            places.Places,
            name="ListPlaces",
        ),
        dependencies.route(
            "/places/{placeId}",
            places.Place,
            name="ViewPlace",
        ),
        # todo: add /legs/types
        # todo: add /legs/{legId}
        # todo: add /segments/{segmentId}/legs
        # todo: add /segments/{segmentId}
        dependencies.route("/trips/searches", trips.TripSearches),
        dependencies.route(
            "/trips/{tripId}",
            trips.Trip,
            name="ViewTrip",
        ),
        # todo: add /trips/{tripId}/segments
        # todo: add /trips/{tripId}/prices
        dependencies.route(
            "/trips/searches/{tripSearchId}",
            trips.TripSearch,
            name="ViewTripSearch",
        ),
        dependencies.route(
            "/trips/searches/{tripSearchId}/trips",
            trips.TripsByTripSearch,
            name="ViewTrips",
        ),
        dependencies.route("/offers/searches", offers.OfferSearches),
        # todo: add /offers/searches/{offerSearchId}
        # todo: add /offers/searches/{offerSearchId}/offers
        # todo: add /offers/searches/{offerSearchId}/related
        # todo: add /orders
        # todo: add /orders/{orderId}
        # todo: add /orders/{orderId}/relationships/offers
    ]
