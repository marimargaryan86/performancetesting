from __future__ import annotations

import abc
import dataclasses
import datetime
import uuid
from typing import Optional

import grpc

from snowfall.adapter.trips import TripsPage
from snowfall.common.v1alpha import models_pb2
from snowfall.junction.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.stdlib.format import protobuf


class NotFoundError(Exception):
    """Raised when a trip search resource is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class TripSearchRequest(object):
    origin: models_pb2.Place
    destination: models_pb2.Place
    departure_after: datetime.datetime


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        trip_search_request: TripSearchRequest,
    ) -> trips_pb2.TripSearch:
        """Create a trip search."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> trips_pb2.TripSearch:
        """Get a trip search."""

    @abc.abstractmethod
    async def list_trips_by_trip_search(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> TripsPage:
        """List trips by trip search."""


class DictClient(Client):
    def __init__(self) -> None:
        self._searches: dict[str, trips_pb2.TripSearch] = {}
        self._trips_cache: dict[str, list[models_pb2.TripReference]] = {}

    async def create(
        self,
        trip_search_request: TripSearchRequest,
    ) -> trips_pb2.TripSearch:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=1,
        )
        trip_search = trips_pb2.TripSearch(
            id=str(uuid.uuid4()),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            origin=trip_search_request.origin,
            destination=trip_search_request.destination,
            departure_after=protobuf.datetime_to_protobuf(
                trip_search_request.departure_after,
            ),
        )
        self._searches[trip_search.id] = trip_search
        await self._generate_trips(trip_search)

        return trip_search

    async def get(self, identifier: str) -> trips_pb2.TripSearch:
        try:
            return self._searches[identifier]
        except KeyError:
            raise NotFoundError()

    async def list_trips_by_trip_search(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> TripsPage:
        try:
            return TripsPage.from_proto(
                trips_pb2.ListTripsResponse(
                    trips=self._trips_cache[identifier],
                ),
            )
        except KeyError:
            raise NotFoundError()

    async def _generate_trips(self, trip_search: trips_pb2.TripSearch) -> None:
        self._trips_cache[trip_search.id] = [
            models_pb2.TripReference(
                id="b3e45af0-f3ae-46e5-a94f-fd1c9d86fb7d",
                segments=[
                    models_pb2.SegmentReference(
                        id=str(uuid.uuid4()),
                        schedule_id=str(uuid.uuid4()),
                        leg_ids=[
                            str(uuid.uuid4()),
                        ],
                    ),
                ],
            ),
        ]


class GrpcClient(Client):
    def __init__(
        self,
        trips: trips_pb2_grpc.TripServiceStub,
        trip_searches: trips_pb2_grpc.TripSearchServiceStub,
    ):
        self._trips = trips
        self._trip_searches = trip_searches

    async def create(
        self,
        trip_search_request: TripSearchRequest,
    ) -> trips_pb2.TripSearch:
        request = trips_pb2.EnqueueTripSearchRequest(
            trip_search=trips_pb2.TripSearch(
                origin=trip_search_request.origin,
                destination=trip_search_request.destination,
                departure_after=protobuf.datetime_to_protobuf(
                    trip_search_request.departure_after,
                ),
            ),
        )

        response = await self._trip_searches.EnqueueTripSearch(request)

        return response.trip_search

    async def get(self, identifier: str) -> trips_pb2.TripSearch:
        try:
            response = await self._trip_searches.GetTripSearchDetails(
                trips_pb2.GetTripSearchDetailsRequest(
                    id=identifier,
                ),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Trip Search with ID '{id}' not found.".format(id=identifier),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.trip_search

    async def list_trips_by_trip_search(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> TripsPage:
        trip_search = await self.get(identifier)

        if not trip_search.trip_ids:
            return TripsPage.from_proto(trips_pb2.ListTripsResponse())

        request = trips_pb2.ListTripsRequest(
            ids=trip_search.trip_ids,
            page_token=cursor or "",
        )

        if limit is not None:
            request.page_size = limit

        response = await self._trips.ListTrips(request)

        return TripsPage.from_proto(response)
