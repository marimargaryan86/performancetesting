from __future__ import annotations

import abc
import dataclasses
import datetime
import uuid

from snowfall.common.v1alpha import models_pb2
from snowfall.format import protobuf
from snowfall.junction.trips.v1alpha import trips_pb2


class NotFoundError(Exception):
    """Raised when a trip search resource is not found."""


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
    ) -> list[models_pb2.TripReference]:
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
            expires_at=await protobuf.datetime_to_protobuf(expires_at),
            origin=trip_search_request.origin,
            destination=trip_search_request.destination,
            departure_after=await protobuf.datetime_to_protobuf(
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
    ) -> list[models_pb2.TripReference]:
        try:
            return self._trips_cache[identifier]
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
                        origin_stop_id="f236a92c-4cfa-468e-85ef-431d25dcd925",
                        destination_stop_id="488a836d-ec22-439b-a9d8-3c4c386a731e",
                    ),
                ],
            ),
        ]
