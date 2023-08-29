from collections.abc import Mapping

import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.go.adapter import legs as legs_adapter
from snowfall.project.junction.go.adapter import locations as locations_adapter
from snowfall.project.junction.go.adapter import (
    offer_searches as offer_searches_adapter,
)
from snowfall.project.junction.go.adapter import offers as offers_adapter
from snowfall.project.junction.go.adapter import places as places_adapter
from snowfall.project.junction.go.adapter import price_quotes as price_quotes_adapter
from snowfall.project.junction.go.adapter import schedules as schedules_adapter
from snowfall.project.junction.go.adapter import segments as segments_adapter
from snowfall.project.junction.go.adapter import (
    trip_candidate_searches as trip_candidate_searches_adapter,
)
from snowfall.project.junction.go.adapter import trips as trips_adapter
from snowfall.project.junction.go.service.client_api import resources
from snowfall.project.junction.go.service.client_api.routes import (
    legs,
    offers,
    orders,
    places,
    segments,
    trips,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2 as orders_pb2
from snowfall.project.junction.go.service.places.v1 import models_pb2 as places_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib.integration.starlette import routes


def get_routes(  # noqa: WPS210
    dependencies: lagom.Container,
    reseller_currencies: Mapping[str, str],
    reseller_pay_companies: Mapping[str, str],
) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)
    place_handler = places.Places(
        dependencies[places_adapter.Client],  # type: ignore[type-abstract]
    )
    segment_handler = segments.Segments(
        dependencies[schedules_adapter.Client],  # type: ignore[type-abstract]
        dependencies[segments_adapter.Client],  # type: ignore[type-abstract]
    )
    offer_searches_handler = offers.OfferSearches(
        _legs_client=dependencies[legs_adapter.Client],  # type: ignore[type-abstract]
        _trips_client=dependencies[trips_adapter.Client],  # type: ignore[type-abstract]
        _offer_search_client=(
            dependencies[offer_searches_adapter.Client]  # type: ignore[type-abstract]
        ),
        _reseller_currencies=reseller_currencies,
        _reseller_pay_companies=reseller_pay_companies,
    )
    price_quotes_handler = offers.PriceQuotes(
        _offers_client=dependencies[offers_adapter.Client],  # type: ignore[type-abstract]
        _price_quotes_client=(
            dependencies[price_quotes_adapter.Client]  # type: ignore[type-abstract]
        ),
        _reseller_pay_companies=reseller_pay_companies,
    )
    trip_candidate_searches_handler = trips.TripCandidateSearches(
        _trip_candidate_searches_client=dependencies[
            trip_candidate_searches_adapter.Client  # type: ignore[type-abstract]
        ],
        _locations_client=dependencies[locations_adapter.Client],  # type: ignore[type-abstract]
        _reseller_currencies=reseller_currencies,
        _reseller_pay_companies=reseller_pay_companies,
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
        routes.to_route(
            "/segments/{segmentId}",
            segment_handler.view,
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
        # TODO: add GET /trips/{tripId}/prices
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
        # TODO: add GET /trips/searches/{tripSearchId}/segments
        integration.route(
            "/trips/searches/{tripSearchId}/trips",
            trips.TripsByTripSearch,
            name="ViewTripsByTripSearch",
        ),
        routes.to_route(
            "/trip-candidates/searches",
            trip_candidate_searches_handler.post,
            methods=["POST"],
        ),
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
        routes.to_route(
            "/offers/searches",
            offer_searches_handler.post,
            methods=["POST"],
        ),
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
        # TODO: add GET /offers/searches/{offerSearchId}/related
        routes.to_route(
            "/offers/quotes",
            price_quotes_handler.post,
            name="CreateOfferQuotes",
            methods=["POST"],
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
            "/bookings/cancellations",
            orders.BookingsCancellation,
            name="CreateBookingsCancellation",
        ),
        integration.route(
            "/bookings/cancellations/{bookingsCancellationId}",
            orders.BookingsCancellation,
            name="ViewBookingsCancellation",
        ),
        integration.route(
            "/bookings/{bookingId}",
            orders.Booking,
            name="ViewBooking",
        ),
        integration.route(
            "/bookings/{bookingId}/cancellation",
            orders.BookingCancellationByBooking,
            name="ViewBookingCancellationByBooking",
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
