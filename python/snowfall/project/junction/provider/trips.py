from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import grpc

from snowfall.project.junction.provider.v2alpha import trips_pb2, trips_pb2_grpc
from snowfall.stdlib.transport.grpc import rich_status, service

if TYPE_CHECKING:
    Implementation = Callable[
        [trips_pb2.SearchTripsRequest],
        Awaitable[trips_pb2.SearchTripsResponse],
    ]


class TripService(service.Service, trips_pb2_grpc.TripServiceServicer):
    def __init__(self, implementation: Implementation):
        self._implementation = implementation

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        trips_pb2_grpc.add_TripServiceServicer_to_server(self, server)

    async def SearchTrips(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.SearchTripsRequest,
        context: grpc.aio.ServicerContext,
    ) -> trips_pb2.SearchTripsResponse:
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

        return await self._implementation(request)
