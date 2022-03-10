from __future__ import annotations

import abc
from typing import Sequence

import grpc

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.trips.v1alpha import trips_pb2, trips_pb2_grpc


class NotFoundError(Exception):
    """Raised when a place is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.TripReference:
        """Fetch a trip resource."""


class DictClient(Client):
    def __init__(self, trips: Sequence[models_pb2.TripReference]) -> None:
        self._trips = {trip.id: trip for trip in trips}

    async def get(self, trip_id: str) -> models_pb2.TripReference:
        if trip_id not in self._trips:
            raise NotFoundError()

        return models_pb2.TripReference(id=trip_id)


class GrpcClient(Client):
    def __init__(self, trips: trips_pb2_grpc.TripServiceStub):
        self._trips = trips

    async def get(self, trip_id: str) -> models_pb2.TripReference:
        try:
            response = await self._trips.GetTrip(trips_pb2.GetTripRequest(id=trip_id))
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Trip with ID '{id}' not found.".format(id=trip_id),
                ) from exc

            raise UnknownError() from exc

        return response.trip
