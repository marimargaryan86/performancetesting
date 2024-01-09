from __future__ import annotations

from collections.abc import Awaitable, Callable, Collection, Iterable
from typing import TYPE_CHECKING, NamedTuple

import grpc

from snowfall.project.junction.provider.v2alpha import (
    meta_pb2,
    trips_pb2,
    trips_pb2_grpc,
)
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.transport.grpc import rich_status, service


class OneWayRequest(NamedTuple):
    request: trips_pb2.SearchTripsRequest.OneWay
    passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger]


class RoundTripRequest(NamedTuple):
    request: trips_pb2.SearchTripsRequest.RoundTrip
    passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger]


class MultiCityRequest(NamedTuple):
    request: trips_pb2.SearchTripsRequest.MultiCity
    passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger]


if TYPE_CHECKING:
    OneWayImplementation = Callable[
        [OneWayRequest],
        Awaitable[trips_pb2.SearchTripsResponse],
    ]
    RoundTripImplementation = Callable[
        [RoundTripRequest],
        Awaitable[trips_pb2.SearchTripsResponse],
    ]
    MultiCityImplementation = Callable[
        [MultiCityRequest],
        Awaitable[trips_pb2.SearchTripsResponse],
    ]


class TripSearchImplementation(NamedTuple):
    stop_identification_method: meta_pb2.TripSearchCapabilities.StopIdentificationMethod.ValueType
    passenger_age_identification_method: meta_pb2.TripSearchCapabilities.PassengerAgeIdentificationMethod.ValueType
    supported_segment_types: Collection[segment_type_pb2.SegmentType.ValueType]
    one_way: OneWayImplementation
    round_trip: RoundTripImplementation | None = None
    multi_city: MultiCityImplementation | None = None

    def is_valid(self) -> bool:
        return not (
            self.stop_identification_method
            == meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_UNSPECIFIED
            or self.passenger_age_identification_method
            == meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_UNSPECIFIED
            or not self.supported_segment_types
            or segment_type_pb2.SEGMENT_TYPE_UNSPECIFIED in self.supported_segment_types
        )


class TripService(service.Service, trips_pb2_grpc.TripServiceServicer):
    def __init__(
        self,
        implementation: TripSearchImplementation,
    ):
        self._implementation = implementation

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        trips_pb2_grpc.add_TripServiceServicer_to_server(self, server)

    def get_capabilities(self) -> meta_pb2.TripSearchCapabilities:
        return meta_pb2.TripSearchCapabilities(
            is_supported=True,
            supports_round_trip=self._implementation.round_trip is not None,
            supports_multi_city=self._implementation.multi_city is not None,
            stop_identification_method=self._implementation.stop_identification_method,
            supported_segment_types=self._implementation.supported_segment_types,
            passenger_age_identification_method=self._implementation.passenger_age_identification_method,
        )

    async def SearchTrips(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.SearchTripsRequest,
        context: grpc.aio.ServicerContext,
    ) -> trips_pb2.SearchTripsResponse:
        await self._validate_request(request, context)

        return await self._perform_search(request, context)

    async def SearchOffers(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.SearchOffersRequest,
        context: grpc.aio.ServicerContext,
    ) -> trips_pb2.SearchOffersResponse:
        return await context.abort(
            grpc.StatusCode.UNIMPLEMENTED,
            "Offer searches are not implemented.",
        )

    async def _validate_request(
        self,
        request: trips_pb2.SearchTripsRequest,
        context: grpc.aio.ServicerContext,
    ) -> None:
        if not request.WhichOneof("search_mode"):
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="search_mode",
                    field_description="Search mode must be chosen",
                    description="Searching requires one search mode",
                ),
            )

        if not request.passengers:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="passengers",
                    field_description="Field must not be empty",
                    description="Searching requires at least one passenger",
                ),
            )

    async def _perform_search(
        self,
        request: trips_pb2.SearchTripsRequest,
        context: grpc.aio.ServicerContext,
    ) -> trips_pb2.SearchTripsResponse:
        match request.WhichOneof("search_mode"):
            case "one_way":
                response = await self._implementation.one_way(
                    OneWayRequest(request.one_way, request.passengers),
                )
            case "round_trip":
                if not self._implementation.round_trip:
                    return await context.abort(
                        grpc.StatusCode.UNIMPLEMENTED,
                        "Roundtrip searches are not implemented.",
                    )

                response = await self._implementation.round_trip(
                    RoundTripRequest(
                        request.round_trip,
                        request.passengers,
                    ),
                )
            case "multi_city":
                if not self._implementation.multi_city:
                    return await context.abort(
                        grpc.StatusCode.UNIMPLEMENTED,
                        "Multi-city searches are not implemented.",
                    )

                response = await self._implementation.multi_city(
                    MultiCityRequest(
                        request.multi_city,
                        request.passengers,
                    ),
                )
            case _:
                response = trips_pb2.SearchTripsResponse()

        return response
