import dataclasses
import uuid

_PLACES = (
    "f236a92c-4cfa-468e-85ef-431d25dcd925",
    "488a836d-ec22-439b-a9d8-3c4c386a731e",
)


@dataclasses.dataclass(frozen=True)
class Place(object):
    identifier: uuid.UUID


class NotFoundError(Exception):
    """Raised when a place is not found."""


class PlaceRepository(object):
    def __init__(self) -> None:
        self._places = {
            place: Place(
                identifier=uuid.UUID(place),
            )
            for place in _PLACES
        }

    async def get(self, place_id: uuid.UUID) -> Place:
        try:
            return self._places[str(place_id)]
        except KeyError:
            raise NotFoundError("Place with ID '{id}' not found.".format(id=place_id))

    async def find(self) -> list[Place]:
        return list(self._places.values())
