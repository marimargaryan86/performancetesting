from __future__ import annotations

import abc
from typing import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.project.junction.go.v1alpha import models_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.TripReference:
        """Fetch a trip resource."""

    @abc.abstractmethod
    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> trips_pb2.ListTripsResponse:
        """Find trips by trip by ID."""


class DictClient(Client):
    def __init__(self, trips: Sequence[models_pb2.TripReference]) -> None:
        self._trips = {trip.id: trip for trip in trips}

    async def get(self, trip_id: str) -> models_pb2.TripReference:
        try:
            return self._trips[trip_id]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> trips_pb2.ListTripsResponse:
        return trips_pb2.ListTripsResponse(
            trips=[trip for trip in self._trips.values() if trip.id in identifiers],
        )


class GrpcClient(Client):
    def __init__(self, trips: trips_pb2_grpc.TripServiceStub, timeout: int = 10):
        self._timeout = timeout
        self._trips = trips

    async def get(self, trip_id: str) -> models_pb2.TripReference:
        response = await errors.handle_grpc_errors(
            self._trips.GetTrip(
                trips_pb2.GetTripRequest(id=trip_id),
                timeout=self._timeout,
            ),
        )

        return response.trip

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> trips_pb2.ListTripsResponse:
        request = trips_pb2.ListTripsRequest(
            ids=list(identifiers),
            page_token=cursor or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._trips.ListTrips(request, timeout=self._timeout),
        )
