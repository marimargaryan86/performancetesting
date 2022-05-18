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
        dependencies.route("/health", health.Health, name="Health"),
        dependencies.route(
            "/places/types",
            places.PlaceTypes,
            name="ListPlaceTypes",
        ),
        dependencies.route(
            "/places/types/{placeTypeId}",
            places.PlaceType,
            name="ViewPlaceType",
        ),
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
        dependencies.route(
            "/legs/types",
            legs.LegTypes,
            name="ListLegTypes",
        ),
        dependencies.route(
            "/legs/types/{legTypeId}",
            legs.LegType,
            name="ViewLegType",
        ),
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
        dependencies.route(
            "/segments/{segmentId}/legs",
            legs.LegsBySegmentId,
            name="ListLegsBySegmentId",
        ),
        dependencies.route("/trips/searches", trips.TripSearches),
        dependencies.route(
            "/trips/{tripId}",
            trips.Trip,
            name="ViewTrip",
        ),
        dependencies.route(
            "/trips/{tripId}/legs",
            legs.LegsByTripId,
            name="ListLegsByTripId",
        ),
        dependencies.route(
            "/trips/{tripId}/segments",
            trips.TripSegments,
            name="ListTripSegments",
        ),
        # todo: add GET /trips/{tripId}/prices
        dependencies.route(
            "/trips/searches/{tripSearchId}",
            trips.TripSearch,
            name="ViewTripSearch",
        ),
        dependencies.route(
            "/trips/searches/{tripSearchId}/legs",
            legs.LegsByTripSearchId,
            name="ListLegsByTripSearchId",
        ),
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
        dependencies.route(
            "/orders",
            orders.Orders,
            name="ListOrders",
        ),
        dependencies.route(
            "/orders/{orderId}",
            orders.Order,
            name="ViewOrder",
        ),
    ]
