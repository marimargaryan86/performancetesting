from __future__ import annotations

import abc
import dataclasses
from typing import Optional, Sequence

import grpc

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.trips.v1alpha import trips_pb2, trips_pb2_grpc


class NotFoundError(Exception):
    """Raised when a trip is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class TripsPage(object):
    trips: Sequence[models_pb2.TripReference]
    next_page_token: Optional[str] = None

    @classmethod
    def from_proto(cls, grpc_trips: trips_pb2.ListTripsResponse) -> TripsPage:
        return cls(
            trips=grpc_trips.trips,
            next_page_token=grpc_trips.next_page_token,
        )


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.TripReference:
        """Fetch a trip resource."""

    @abc.abstractmethod
    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> TripsPage:
        """Find trips by trip by ID."""


class DictClient(Client):
    def __init__(self, trips: Sequence[models_pb2.TripReference]) -> None:
        self._trips = {trip.id: trip for trip in trips}

    async def get(self, trip_id: str) -> models_pb2.TripReference:
        try:
            return self._trips[trip_id]
        except KeyError as err:
            raise NotFoundError() from err

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> TripsPage:
        return TripsPage(
            trips=[trip for trip in self._trips.values() if trip.id in identifiers],
        )


class GrpcClient(Client):
    def __init__(self, trips: trips_pb2_grpc.TripServiceStub, timeout: int = 10):
        self._timeout = timeout
        self._trips = trips

    async def get(self, trip_id: str) -> models_pb2.TripReference:
        try:
            response = await self._trips.GetTrip(
                trips_pb2.GetTripRequest(id=trip_id),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Trip with ID '{id}' not found.".format(id=trip_id),
                ) from exc

            raise UnknownError() from exc

        return response.trip

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> TripsPage:
        request = trips_pb2.ListTripsRequest(
            ids=list(identifiers),
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        try:
            response = await self._trips.ListTrips(request, timeout=self._timeout)
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc

        return TripsPage(
            trips=list(response.trips),
            next_page_token=response.next_page_token,
        )
