from __future__ import annotations

from collections.abc import Awaitable, Callable, Collection, Iterable
from typing import TYPE_CHECKING, Literal, NamedTuple

import grpc

from snowfall.project.junction.provider.v2alpha import (
    meta_pb2,
    trips_pb2,
    trips_pb2_grpc,
)
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.transport.grpc import rich_status, service

if TYPE_CHECKING:
    TripSearchOneWayImplementation = Callable[
        [
            trips_pb2.SearchTripsRequest.OneWay,
            Iterable[trips_pb2.SearchTripsRequest.Passenger],
        ],
        Awaitable[trips_pb2.SearchTripsResponse],
    ]
    TripSearchRoundTripImplementation = Callable[
        [
            trips_pb2.SearchTripsRequest.RoundTrip,
            Iterable[trips_pb2.SearchTripsRequest.Passenger],
        ],
        Awaitable[trips_pb2.SearchTripsResponse],
    ]
    TripSearchMultiCityImplementation = Callable[
        [
            trips_pb2.SearchTripsRequest.MultiCity,
            Iterable[trips_pb2.SearchTripsRequest.Passenger],
        ],
        Awaitable[trips_pb2.SearchTripsResponse],
    ]
    OfferSearchOneWayImplementation = Callable[
        [
            trips_pb2.SearchOffersRequest.OneWay,
            Iterable[trips_pb2.SearchOffersRequest.Passenger],
        ],
        Awaitable[trips_pb2.SearchOffersResponse],
    ]
    OfferSearchRoundTripImplementation = Callable[
        [
            trips_pb2.SearchOffersRequest.RoundTrip,
            Iterable[trips_pb2.SearchOffersRequest.Passenger],
        ],
        Awaitable[trips_pb2.SearchOffersResponse],
    ]
    OfferSearchMultiCityImplementation = Callable[
        [
            trips_pb2.SearchOffersRequest.MultiCity,
            Iterable[trips_pb2.SearchOffersRequest.Passenger],
        ],
        Awaitable[trips_pb2.SearchOffersResponse],
    ]


class TripSearchImplementation(NamedTuple):
    stop_identification_method: (
        meta_pb2.TripSearchCapabilities.StopIdentificationMethod.ValueType
    )
    passenger_age_identification_method: (
        meta_pb2.TripSearchCapabilities.PassengerAgeIdentificationMethod.ValueType
    )
    supported_segment_types: Collection[segment_type_pb2.SegmentType.ValueType]
    one_way: TripSearchOneWayImplementation
    round_trip: TripSearchRoundTripImplementation | None = None
    multi_city: TripSearchMultiCityImplementation | None = None

    def is_valid(self) -> bool:
        return not (
            self.stop_identification_method
            == meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_UNSPECIFIED
            or self.passenger_age_identification_method
            == meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_UNSPECIFIED
            or not self.supported_segment_types
            or segment_type_pb2.SEGMENT_TYPE_UNSPECIFIED in self.supported_segment_types
        )


class OfferSearchImplementation(NamedTuple):
    one_way: OfferSearchOneWayImplementation
    round_trip: OfferSearchRoundTripImplementation | None = None
    multi_city: OfferSearchMultiCityImplementation | None = None


class TripService(service.Service, trips_pb2_grpc.TripServiceServicer):
    def __init__(
        self,
        trip_search: TripSearchImplementation,
        offer_search: OfferSearchImplementation | None = None,
    ):
        self._trip_search = trip_search
        self._offer_search = offer_search

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        trips_pb2_grpc.add_TripServiceServicer_to_server(self, server)

    def get_capabilities(self) -> meta_pb2.TripSearchCapabilities:
        return meta_pb2.TripSearchCapabilities(
            is_supported=self._is_supported,
            supports_round_trip=self._supports_round_trip,
            supports_multi_city=self._supports_multi_city,
            stop_identification_method=self._trip_search.stop_identification_method,
            supported_segment_types=self._trip_search.supported_segment_types,
            passenger_age_identification_method=self._trip_search.passenger_age_identification_method,
        )

    async def SearchTrips(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.SearchTripsRequest,
        context: grpc.aio.ServicerContext,
    ) -> trips_pb2.SearchTripsResponse:
        await self._validate_request(request, context)
        search_mode = await _get_search_mode(request, context)
        search_function = getattr(self._trip_search, search_mode)

        if not search_function:
            return await context.abort(
                grpc.StatusCode.UNIMPLEMENTED,
                "Search mode '{0}' is not implemented.".format(search_mode),
            )

        return await search_function(getattr(request, search_mode), request.passengers)

    async def SearchOffers(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.SearchOffersRequest,
        context: grpc.aio.ServicerContext,
    ) -> trips_pb2.SearchOffersResponse:
        if not self._offer_search:
            return await context.abort(
                grpc.StatusCode.UNIMPLEMENTED,
                "Offer searches are not implemented.",
            )

        await self._validate_request(request, context)
        search_mode = await _get_search_mode(request, context)
        search_function = getattr(self._offer_search, search_mode)

        if not search_function:
            return await context.abort(
                grpc.StatusCode.UNIMPLEMENTED,
                "Search mode '{0}' is not implemented.".format(search_mode),
            )

        return await search_function(getattr(request, search_mode), request.passengers)

    async def _validate_request(
        self,
        request: trips_pb2.SearchTripsRequest | trips_pb2.SearchOffersRequest,
        context: grpc.aio.ServicerContext,
    ) -> None:
        if not request.passengers:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="passengers",
                    field_description="Field must not be empty",
                    description="Searching requires at least one passenger",
                ),
            )

    @property
    def _is_supported(self) -> bool:
        return True  # Hardcode this until it is a requirement to have offers and orders

    @property
    def _supports_round_trip(self) -> bool:
        return self._trip_search.round_trip is not None and (
            not self._offer_search or self._offer_search.round_trip is not None
        )

    @property
    def _supports_multi_city(self) -> bool:
        return self._trip_search.multi_city is not None and (
            not self._offer_search or self._offer_search.multi_city is not None
        )


async def _get_search_mode(
    request: trips_pb2.SearchTripsRequest | trips_pb2.SearchOffersRequest,
    context: grpc.aio.ServicerContext,
) -> Literal["one_way", "round_trip", "multi_city"]:
    search_mode = request.WhichOneof("search_mode")

    if not search_mode:
        return await rich_status.abort_with_rich_status(
            context=context,
            status=rich_status.build_bad_request(
                field_name="search_mode",
                field_description="Search mode must be chosen",
                description="Searching requires one search mode",
            ),
        )

    return search_mode
