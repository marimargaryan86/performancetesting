from lagom.integrations import starlette
from starlette import routing

from snowfall.junction.client_api.routes import (
    health,
    legs,
    offers,
    orders,
    places,
    segments,
    trips,
)


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
        dependencies.route(
            "/legs/{legId}",
            legs.Leg,
            name="ViewLeg",
        ),
        dependencies.route(
            "/segments/{segmentId}",
            segments.Segment,
            name="ViewSegment",
        ),
        # todo: add GET /segments/{segmentId}/legs
        dependencies.route("/trips/searches", trips.TripSearches),
        dependencies.route(
            "/trips/{tripId}",
            trips.Trip,
            name="ViewTrip",
        ),
        # todo: add GET /trips/{tripId}/legs
        dependencies.route(
            "/trips/{tripId}/segments",
            trips.TripSegments,
            name="ViewTripSegments",
        ),
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
            name="ViewTripsByTripSearch",
        ),
        dependencies.route("/offers/searches", offers.OfferSearches),
        dependencies.route(
            "/offers/searches/{offerSearchId}",
            offers.OfferSearch,
            name="ViewOfferSearch",
        ),
        dependencies.route(
            "/offers/searches/{offerSearchId}/offers",
            offers.OffersByOfferSearch,
            name="ViewOffersByOfferSearch",
        ),
        # todo: add GET /offers/searches/{offerSearchId}/related
        dependencies.route(
            "/offers/{offerId}",
            offers.Offer,
            name="ViewOffer",
        ),
        dependencies.route("/orders", orders.Orders),
        # todo: add GET /orders
        dependencies.route(
            "/orders/{orderId}",
            orders.Order,
            name="ViewOrder",
        ),
        # todo: add POST /orders/{orderId}/relationships/offers
    ]
