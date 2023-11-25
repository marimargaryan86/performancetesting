from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable
from typing import TYPE_CHECKING, NamedTuple

import grpc

from snowfall.project.junction.provider.v2alpha import trips_pb2, trips_pb2_grpc
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


class TripService(service.Service, trips_pb2_grpc.TripServiceServicer):
    def __init__(
        self,
        one_way: OneWayImplementation,
        round_trip: RoundTripImplementation | None = None,
        multi_city: MultiCityImplementation | None = None,
    ):
        self._one_way = one_way
        self._round_trip = round_trip
        self._multi_city = multi_city

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        trips_pb2_grpc.add_TripServiceServicer_to_server(self, server)

    async def SearchTrips(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.SearchTripsRequest,
        context: grpc.aio.ServicerContext,
    ) -> trips_pb2.SearchTripsResponse:
        await self._validate_request(request, context)

        return await self._perform_search(request, context)

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
                response = await self._one_way(
                    OneWayRequest(request.one_way, request.passengers),
                )
            case "round_trip":
                if not self._round_trip:
                    return await context.abort(
                        grpc.StatusCode.UNIMPLEMENTED,
                        "Roundtrip searches are not implemented.",
                    )

                response = await self._round_trip(
                    RoundTripRequest(
                        request.round_trip,
                        request.passengers,
                    ),
                )
            case "multi_city":
                if not self._multi_city:
                    return await context.abort(
                        grpc.StatusCode.UNIMPLEMENTED,
                        "Multi-city searches are not implemented.",
                    )

                response = await self._multi_city(
                    MultiCityRequest(
                        request.multi_city,
                        request.passengers,
                    ),
                )
            case _:
                response = trips_pb2.SearchTripsResponse()

        return response
