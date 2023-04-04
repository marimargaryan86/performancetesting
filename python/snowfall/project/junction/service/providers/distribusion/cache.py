import datetime
from typing import Type

from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class PassengerType(RedisRecord):
    type_name: str
    type_code: str
    min_age: int
    max_age: int


class FareRule(RedisRecord):
    name: str
    description: str


class OfferDetails(RedisRecord):
    expires_at: datetime.datetime
    currency: str
    price: int
    fare_class: str
    passenger_types: list[PassengerType]
    fully_refundable: bool | None
    non_refundable: bool | None
    changeable: bool | None
    fare_rules: list[FareRule] | None


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in cache."""

    _record_type: Type[OfferDetails] = OfferDetails
