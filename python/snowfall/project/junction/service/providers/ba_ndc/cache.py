import datetime
import uuid
from collections.abc import Sequence

from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class Price(RedisRecord):
    amount: str
    currency: str


class PriceBreakdown(RedisRecord):
    currency: str
    base_amount: str
    tax_amount: str


class OfferPenalty(RedisRecord):
    penalty_type: str
    price: Price


class OfferDetailsPassenger(RedisRecord):
    identifier: str
    passenger_type: str | None


class OfferDetails(RedisRecord):
    offer_id: uuid.UUID
    is_international_flight: bool
    has_flight_with_usa_destination: bool
    expires_at: datetime.datetime


class PriceQuoteDetails(RedisRecord):
    offer_id: uuid.UUID
    passengers: Sequence[OfferDetailsPassenger]
    price: Price
    price_breakdown: PriceBreakdown
    is_international_flight: bool
    has_flight_with_usa_destination: bool
    expires_at: datetime.datetime
    penalties: Sequence[OfferPenalty]


class OfferCache(RedisRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: type[OfferDetails] = OfferDetails


class PriceQuoteCache(RedisRepository[PriceQuoteDetails]):
    """Stores price quotes in the cache."""

    _record_type: type[PriceQuoteDetails] = PriceQuoteDetails
