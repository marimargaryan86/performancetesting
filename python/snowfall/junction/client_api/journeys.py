from __future__ import annotations

import dataclasses
import datetime
import uuid

import pydantic
from starlette import requests

from snowfall.adapter import places
from snowfall.junction.client_api import models


class NotFoundError(Exception):
    """Raised when a journey resource is not found."""


@dataclasses.dataclass(frozen=True)
class JourneySearch(object):
    identifier: uuid.UUID
    expires_at: datetime.datetime
    origin: places.Place
    destination: places.Place
    departure_after: datetime.datetime


class JourneySearchRequest(models.BaseModel):
    origin: places.Place
    destination: places.Place
    departure_after: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
    )


class JourneySearchResource(models.Resource):
    @classmethod
    async def from_data_class(
        cls,
        journey_search: JourneySearch,
        request: requests.Request,
    ) -> JourneySearchResource:
        return cls(
            id=str(journey_search.identifier),
            type="journey-searches",
            attributes={
                "expiresAt": journey_search.expires_at,
                "departureAfter": journey_search.departure_after,
            },
            relationships={
                "origin": {
                    "data": {
                        "id": str(journey_search.origin.identifier),
                        "type": "places",
                    },
                },
                "destination": {
                    "data": {
                        "id": str(journey_search.destination.identifier),
                        "type": "places",
                    },
                },
            },
            links={
                "self": request.url_for(
                    "ViewJourneySearch",
                    journeySearchId=journey_search.identifier,
                ),
            },
        )


class JourneySearchRepository(object):
    def __init__(self) -> None:
        self._searches: dict[uuid.UUID, JourneySearch] = {}

    async def create(
        self,
        journey_search_request: JourneySearchRequest,
    ) -> JourneySearch:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=1,
        )
        journey_search = JourneySearch(
            identifier=uuid.uuid4(),
            expires_at=expires_at,
            origin=journey_search_request.origin,
            destination=journey_search_request.destination,
            departure_after=journey_search_request.departure_after,
        )
        self._searches[journey_search.identifier] = journey_search

        return journey_search

    async def get(self, identifier: uuid.UUID) -> JourneySearch:
        try:
            return self._searches[identifier]
        except KeyError:
            raise NotFoundError()
