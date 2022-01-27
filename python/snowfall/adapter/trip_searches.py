from __future__ import annotations

import abc
import dataclasses
import datetime
import uuid

from snowfall.adapter import places


class NotFoundError(Exception):
    """Raised when a trip search resource is not found."""


@dataclasses.dataclass(frozen=True)
class TripSearch(object):
    identifier: uuid.UUID
    expires_at: datetime.datetime
    origin: places.Place
    destination: places.Place
    departure_after: datetime.datetime


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
    def __init__(self) -> None:
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
        )
        self._searches[trip_search.identifier] = trip_search

        return trip_search

    async def get(self, identifier: uuid.UUID) -> TripSearch:
        try:
            return self._searches[identifier]
        except KeyError:
            raise NotFoundError()
