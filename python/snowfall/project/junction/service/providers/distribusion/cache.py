import datetime

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
    departure_station: str
    arrival_station: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    marketing_carrier: str
    passengers_age: list[int]
    currency: str
    price: int
    fare_class: str
    passenger_types: list[PassengerType]
    fully_refundable: bool | None
    non_refundable: bool | None
    changeable: bool | None
    has_exchange_conditions: bool | None
    fare_rules: list[FareRule] | None


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in cache."""

    _record_type: type[OfferDetails] = OfferDetails


class PriceQuote(RedisRecord):
    expires_at: datetime.datetime
    price: int
    currency: str
    passenger_types: list[PassengerType]
    fare_class: str


class PriceQuoteCache(RedisRepository[PriceQuote]):
    """Stores price quotes in the cache."""

    _record_type: type[PriceQuote] = PriceQuote
