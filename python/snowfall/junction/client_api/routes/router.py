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
        # todo: add GET /legs/types
        # todo: add GET /legs/types/{legTypeId}
        # todo: add GET /legs/{legId}
        # todo: add GET /segments/{segmentId}
        # todo: add GET /segments/{segmentId}/legs
        dependencies.route("/trips/searches", trips.TripSearches),
        dependencies.route(
            "/trips/{tripId}",
            trips.Trip,
            name="ViewTrip",
        ),
        # todo: add GET /trips/{tripId}/legs
        # todo: add GET /trips/{tripId}/segments
        # todo: add GET /trips/{tripId}/prices
        dependencies.route(
            "/trips/searches/{tripSearchId}",
            trips.TripSearch,
            name="ViewTripSearch",
        ),
        # todo: add GET /trips/searches/{tripSearchId}/legs
        # todo: add GET /trips/searches/{tripSearchId}/segments
        dependencies.route(
            "/trips/searches/{tripSearchId}/trips",
            trips.TripsByTripSearch,
            name="ViewTrips",
        ),
        dependencies.route("/offers/searches", offers.OfferSearches),
        # todo: add GET /offers/searches/{offerSearchId}
        # todo: add GET /offers/searches/{offerSearchId}/offers
        # todo: add GET /offers/searches/{offerSearchId}/related
        # todo: add GET /offers/{offerId}
        # todo: add POST /orders
        # todo: add GET /orders
        # todo: add GET /orders/{orderId}
        # todo: add POST /orders/{orderId}/relationships/offers
    ]
