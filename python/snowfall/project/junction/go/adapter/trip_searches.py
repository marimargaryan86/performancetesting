from __future__ import annotations

import abc
import dataclasses
import datetime
from typing import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2


@dataclasses.dataclass(frozen=True)
class TripSearchRequest(object):
    origins: Sequence[models_pb2.Point]
    destinations: Sequence[models_pb2.Point]
    departure_after: datetime.datetime
    maximum_connections: int | None
    allowed_segment_types: Sequence[models_pb2.Schedule.Type.ValueType]


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
        limit: int | None = None,
        cursor: str | None = None,
    ) -> trips_pb2.ListTripsResponse:
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
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            origins=trip_search_request.origins,
            destinations=trip_search_request.destinations,
            departure_after=protobuf.datetime_to_protobuf_datetime(
                trip_search_request.departure_after,
            ),
            maximum_connections=trip_search_request.maximum_connections,
            allowed_segment_types=trip_search_request.allowed_segment_types,
        )
        self._searches[trip_search.id] = trip_search
        await self._generate_trips(trip_search)

        return trip_search

    async def get(self, identifier: str) -> trips_pb2.TripSearch:
        try:
            return self._searches[identifier]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def list_trips_by_trip_search(
        self,
        identifier: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> trips_pb2.ListTripsResponse:
        try:
            return trips_pb2.ListTripsResponse(
                trips=self._trips_cache[identifier],
            )
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def _generate_trips(self, trip_search: trips_pb2.TripSearch) -> None:
        self._trips_cache[trip_search.id] = [
            models_pb2.TripReference(
                id="b3e45af0-f3ae-46e5-a94f-fd1c9d86fb7d",
                segments=[
                    models_pb2.SegmentReference(
                        id=string.uuid(),
                        schedule_id=string.uuid(),
                        leg_ids=[
                            string.uuid(),
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
        timeout: int = 10,
    ):
        self._timeout = timeout
        self._trips = trips
        self._trip_searches = trip_searches

    async def create(
        self,
        trip_search_request: TripSearchRequest,
    ) -> trips_pb2.TripSearch:
        request = trips_pb2.EnqueueTripSearchRequest(
            trip_search=trips_pb2.TripSearch(
                origins=trip_search_request.origins,
                destinations=trip_search_request.destinations,
                departure_after=protobuf.datetime_to_protobuf_datetime(
                    trip_search_request.departure_after,
                ),
                maximum_connections=trip_search_request.maximum_connections,
                allowed_segment_types=trip_search_request.allowed_segment_types,
            ),
        )

        response = await errors.handle_grpc_errors(
            self._trip_searches.EnqueueTripSearch(
                request,
                timeout=self._timeout,
            ),
        )

        return response.trip_search

    async def get(self, identifier: str) -> trips_pb2.TripSearch:
        response = await errors.handle_grpc_errors(
            self._trip_searches.GetTripSearchDetails(
                trips_pb2.GetTripSearchDetailsRequest(
                    id=identifier,
                ),
                timeout=self._timeout,
            ),
        )

        return response.trip_search

    async def list_trips_by_trip_search(
        self,
        identifier: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> trips_pb2.ListTripsResponse:
        trip_search = await self.get(identifier)

        if not trip_search.trip_ids:
            return trips_pb2.ListTripsResponse()

        request = trips_pb2.ListTripsRequest(
            ids=trip_search.trip_ids,
            page_token=cursor or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._trips.ListTrips(request, timeout=self._timeout),
        )
