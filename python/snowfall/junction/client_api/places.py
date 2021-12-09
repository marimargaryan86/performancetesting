from __future__ import annotations

import dataclasses
import uuid
from typing import Any, Mapping, Sequence

from snowfall.junction.client_api import models


class NotFoundError(Exception):
    """Raised when a place is not found."""


@dataclasses.dataclass(frozen=True)
class Place(object):
    identifier: uuid.UUID


class PlaceResource(models.Resource):
    @classmethod
    async def from_data_class(cls, place: Place) -> PlaceResource:
        return cls(id=str(place.identifier), type="places", attributes={})


def _create_db(places: Sequence[Mapping[str, Any]]) -> dict[str, Place]:
    return {
        place["id"]: Place(
            identifier=uuid.UUID(place["id"]),
        )
        for place in places
    }


class PlaceRepository(object):
    def __init__(self, places: Sequence[Mapping[str, Any]]):
        self._places = _create_db(places)

    async def get(self, place_id: uuid.UUID) -> Place:
        try:
            return self._places[str(place_id)]
        except KeyError:
            raise NotFoundError("Place with ID '{id}' not found.".format(id=place_id))

    async def find(self) -> list[Place]:
        return list(self._places.values())
