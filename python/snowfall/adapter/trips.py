import abc
import dataclasses
import datetime
import uuid


class NotFoundError(Exception):
    """Raised when a trip search resource is not found."""


@dataclasses.dataclass(frozen=True)
class Trip(object):
    identifier: uuid.UUID
    expires_at: datetime.datetime


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: uuid.UUID) -> Trip:
        """Get a trip."""


class DictClient(Client):
    def __init__(self) -> None:
        self._trips: dict[uuid.UUID, Trip] = {}

    async def add(self, trip: Trip) -> Trip:
        self._trips[trip.identifier] = trip

        return trip

    async def get(self, identifier: uuid.UUID) -> Trip:
        try:
            return self._trips[identifier]
        except KeyError:
            raise NotFoundError()
