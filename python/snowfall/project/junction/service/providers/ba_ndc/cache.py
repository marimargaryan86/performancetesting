import datetime
import uuid
from typing import List, Type

from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class Price(RedisRecord):
    amount: str
    currency: str


class OfferPenalty(RedisRecord):
    penalty_type: str
    price: Price


class OfferDetailsPassenger(RedisRecord):
    identifier: str
    passenger_type: str | None


class OfferDetails(RedisRecord):
    offer_id: uuid.UUID
    passengers: List[OfferDetailsPassenger]
    price: Price
    international_flight: bool = False
    return_flight_to_usa: bool = False
    expires_at: datetime.datetime
    penalties: List[OfferPenalty]


class OfferCache(RedisRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: Type[OfferDetails] = OfferDetails
