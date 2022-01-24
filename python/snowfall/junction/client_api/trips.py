from __future__ import annotations

import dataclasses
import datetime
import uuid

import pydantic
from starlette import requests

from snowfall.adapter import places
from snowfall.junction.client_api import models


class NotFoundError(Exception):
    """Raised when a trip resource is not found."""


@dataclasses.dataclass(frozen=True)
class Trip(object):
    identifier: uuid.UUID
    expires_at: datetime.datetime


class TripResource(models.Resource):
    @classmethod
    async def from_data_class(
        cls,
        trip: Trip,
    ) -> TripResource:
        return cls(
            id=str(trip.identifier),
            type="trips",
            attributes={
                "expiresAt": trip.expires_at,
            },
            relationships={
                "segments": {
                    "data": [],
                },
            },
            links={
                "self": "/trips/{id}".format(id=trip.identifier),
            },
        )


@dataclasses.dataclass(frozen=True)
class TripSearch(object):
    identifier: uuid.UUID
    expires_at: datetime.datetime
    origin: places.Place
    destination: places.Place
    departure_after: datetime.datetime


class TripSearchRequest(models.BaseModel):
    origin: places.Place
    destination: places.Place
    departure_after: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
    )


class TripSearchResource(models.Resource):
    @classmethod
    async def from_data_class(
        cls,
        trip_search: TripSearch,
        request: requests.Request,
    ) -> TripSearchResource:
        return cls(
            id=str(trip_search.identifier),
            type="trip-searches",
            attributes={
                "expiresAt": trip_search.expires_at,
                "departureAfter": trip_search.departure_after,
            },
            relationships={
                "origin": {
                    "data": {
                        "id": str(trip_search.origin.identifier),
                        "type": "places",
                    },
                },
                "destination": {
                    "data": {
                        "id": str(trip_search.destination.identifier),
                        "type": "places",
                    },
                },
            },
            links={
                "self": request.url_for(
                    "ViewTripSearch",
                    tripSearchId=trip_search.identifier,
                ),
            },
        )


class TripSearchRepository(object):
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
