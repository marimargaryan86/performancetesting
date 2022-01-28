from __future__ import annotations

import abc
import dataclasses
import datetime
import uuid
from typing import Sequence

from snowfall.adapter import places, trips


class NotFoundError(Exception):
    """Raised when a trip search resource is not found."""


@dataclasses.dataclass(frozen=True)
class TripSearch(object):
    identifier: uuid.UUID
    expires_at: datetime.datetime
    origin: places.Place
    destination: places.Place
    departure_after: datetime.datetime
    trips: Sequence[trips.Trip]


@dataclasses.dataclass(frozen=True)
class TripSearchRequest(object):
    origin: places.Place
    destination: places.Place
    departure_after: datetime.datetime


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        trip_search_request: TripSearchRequest,
    ) -> TripSearch:
        """Create a trip search."""

    @abc.abstractmethod
    async def get(self, identifier: uuid.UUID) -> TripSearch:
        """Get a trip search."""


class DictClient(Client):
    def __init__(self, trips_client: trips.DictClient):
        self._trips = trips_client
        self._searches: dict[uuid.UUID, TripSearch] = {}

    async def create(
        self,
        trip_search_request: TripSearchRequest,
    ) -> TripSearch:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=1,
        )
        trip_search = TripSearch(
            identifier=uuid.uuid4(),
            expires_at=expires_at,
            origin=trip_search_request.origin,
            destination=trip_search_request.destination,
            departure_after=trip_search_request.departure_after,
            trips=await self._generate_trips(expires_at),
        )
        self._searches[trip_search.identifier] = trip_search

        return trip_search

    async def get(self, identifier: uuid.UUID) -> TripSearch:
        try:
            return self._searches[identifier]
        except KeyError:
            raise NotFoundError()

    async def _generate_trips(self, expires_at: datetime.datetime) -> list[trips.Trip]:
        return [
            await self._trips.add(
                trips.Trip(
                    identifier=uuid.uuid4(),
                    expires_at=expires_at,
                ),
            ),
        ]
