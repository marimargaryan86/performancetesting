import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.go.adapter import places as places_adapter
from snowfall.project.junction.go.service.client_api import resources
from snowfall.project.junction.go.service.client_api.routes import (
    legs,
    offers,
    orders,
    places,
    segments,
    trips,
)
from snowfall.project.junction.service.orders.v1alpha import models_pb2 as orders_pb2
from snowfall.project.junction.service.places.v1alpha import models_pb2 as places_pb2
from snowfall.stdlib.integration.starlette import routes
from snowfall.stdlib.v1alpha import models_pb2


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)
    place_handler = places.Places(
        dependencies[places_adapter.Client],  # type: ignore[type-abstract]
    )

    return [
        *routes.ListAndViewEnum(
            enum=places_pb2.Location.Type,
            resource_factory=resources.PlaceTypeResource.from_proto,
            path="/places/types",
        ).to_routes(),
        routes.to_route(
            "/places",
            place_handler.list_,
            name="ListPlaces",
        ),
        routes.to_route(
            "/places/{placeId}",
            place_handler.view,
            name="ViewPlace",
        ),
        *routes.ListAndViewEnum(
            enum=models_pb2.Schedule.Type,
            resource_factory=resources.LegTypeResource.from_proto,
            path="/legs/types",
        ).to_routes(),
        integration.route(
            "/legs/{legId}",
            legs.Leg,
            name="ViewLeg",
        ),
        integration.route(
            "/segments/{segmentId}",
            segments.Segment,
            name="ViewSegment",
        ),
        integration.route(
            "/segments/{segmentId}/legs",
            legs.LegsBySegmentId,
            name="ListLegsBySegmentId",
        ),
        integration.route("/trips/searches", trips.TripSearches),
        integration.route(
            "/trips/{tripId}",
            trips.Trip,
            name="ViewTrip",
        ),
        integration.route(
            "/trips/{tripId}/legs",
            legs.LegsByTripId,
            name="ListLegsByTripId",
        ),
        integration.route(
            "/trips/{tripId}/segments",
            trips.TripSegments,
            name="ListTripSegments",
        ),
        # todo: add GET /trips/{tripId}/prices
        integration.route(
            "/trips/searches/{tripSearchId}",
            trips.TripSearch,
            name="ViewTripSearch",
        ),
        integration.route(
            "/trips/searches/{tripSearchId}/legs",
            legs.LegsByTripSearchId,
            name="ListLegsByTripSearchId",
        ),
        # todo: add GET /trips/searches/{tripSearchId}/segments
        integration.route(
            "/trips/searches/{tripSearchId}/trips",
            trips.TripsByTripSearch,
            name="ViewTripsByTripSearch",
        ),
        integration.route("/trip-candidates/searches", trips.TripCandidateSearches),
        integration.route(
            "/trip-candidates/searches/{tripCandidateSearchId}",
            trips.TripCandidateSearch,
            name="ViewTripCandidateSearch",
        ),
        integration.route(
            "/trip-candidates/searches/{tripCandidateSearchId}/offers",
            trips.TripCandidatesByTripCandidateSearch,
            name="ViewTripCandidatesByTripCandidateSearch",
        ),
        integration.route("/offers/searches", offers.OfferSearches),
        integration.route(
            "/offers/searches/{offerSearchId}",
            offers.OfferSearch,
            name="ViewOfferSearch",
        ),
        integration.route(
            "/offers/searches/{offerSearchId}/offers",
            offers.OffersByOfferSearch,
            name="ViewOffersByOfferSearch",
        ),
        # todo: add GET /offers/searches/{offerSearchId}/related
        integration.route(
            "/offers/quotes",
            offers.PriceQuotes,
            name="CreateOfferQuotes",
        ),
        integration.route(
            "/offers/quotes/{offerPriceQuoteId}",
            offers.PriceQuote,
            name="ViewPriceQuote",
        ),
        integration.route(
            "/offers/{offerId}",
            offers.Offer,
            name="ViewOffer",
        ),
        integration.route(
            "/offers/{offerId}/groups",
            offers.OfferGroupsByOffer,
            name="ListOfferGroupsByOffer",
        ),
        # TripOfferGroup
        integration.route(
            "/offers/groups/{offerGroupId}",
            offers.OfferGroup,
            name="ViewOfferGroup",
        ),
        integration.route(
            "/offers/groups/details/{offerGroupDetailsId}",
            offers.OfferGroupDetails,
            name="ViewOfferGroupDetails",
        ),
        integration.route(
            "/offers/groups/{offerGroupId}/details",
            offers.OfferGroupDetailsByOfferGroup,
            name="ListOfferGroupDetailsByOfferGroup",
        ),
        integration.route(
            "/offers/options/{offerOptionId}",
            offers.OfferOption,
            name="ViewOfferOption",
        ),
        integration.route(
            "/offers/groups/{offerGroupId}/options",
            offers.OfferOptionsByOfferGroup,
            name="ListOfferOptionsByOfferGroup",
        ),
        integration.route(
            "/offers/options/details/{offerOptionDetailsId}",
            offers.OfferOptionDetails,
            name="ViewOfferOptionDetails",
        ),
        integration.route(
            "/offers/options/{offerOptionId}/details",
            offers.OfferOptionDetailsByOfferOption,
            name="ListOfferOptionDetailsByOfferOption",
        ),
        integration.route(
            "/journeys",
            orders.Journeys,
            name="ListJourneys",
        ),
        integration.route(
            "/journeys/{journeyId}",
            orders.Journey,
            name="ViewJourney",
        ),
        integration.route(
            "/journeys/{journeyId}/orders",
            orders.OrdersByJourney,
            name="ListOrdersByJourney",
        ),
        integration.route(
            "/orders",
            orders.Orders,
            name="ListOrders",
        ),
        integration.route(
            "/orders/{orderId}",
            orders.Order,
            name="ViewOrder",
        ),
        integration.route(
            "/orders/{orderId}/bookings",
            orders.BookingsByOrder,
            name="ListBookingsByOrder",
        ),
        integration.route(
            "/bookings/{bookingId}",
            orders.Booking,
            name="ViewBooking",
        ),
        integration.route(
            "/bookings/{bookingId}/details",
            orders.BookingDetailsByBooking,
            name="ListDetailsByBooking",
        ),
        integration.route(
            "/bookings/details/{bookingDetailsId}",
            orders.BookingDetails,
            name="ViewBookingDetails",
        ),
        *routes.ListAndViewEnum(
            enum=orders_pb2.Passenger.Gender,
            resource_factory=resources.PassengerGenderResource.from_proto,
            path="/passengers/genders",
        ).to_routes(),
        *routes.ListAndViewEnum(
            enum=orders_pb2.Passenger.Title,
            resource_factory=resources.PassengerTitleResource.from_proto,
            path="/passengers/titles",
        ).to_routes(),
        *routes.ListAndViewEnum(
            enum=models_pb2.CabinClass.Type,
            resource_factory=resources.CabinClassResource.from_proto,
            path="/cabin-classes",
        ).to_routes(),
    ]
