from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetails(RedisRecord):
    search_id: str
    itinerary_id: str
    brand_id: str | None = None


class OfferCache(RedisRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: type[OfferDetails] = OfferDetails


class PriceQuote(RedisRecord):
    pricing_id: str
    transaction_id: str


class PriceQuoteCache(RedisRepository[PriceQuote]):
    """Stores price quotes in the cache."""

    _record_type: type[PriceQuote] = PriceQuote
