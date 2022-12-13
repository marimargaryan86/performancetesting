from typing import Type

from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetails(RedisRecord):
    search_id: str
    search_result_id: int
    transfer_id: int
    fare_id: int
    price: str
    currency: str


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in cache."""

    _record_type: Type[OfferDetails] = OfferDetails


class PriceQuote(RedisRecord):
    search_id: str
    search_result_id: int
    transfer_id: int
    fare_id: int


class PriceQuoteCache(RedisRepository[PriceQuote]):
    """Stores price quotes in the cache."""

    _record_type: Type[PriceQuote] = PriceQuote
