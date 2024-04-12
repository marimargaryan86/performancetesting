from collections.abc import Sequence

from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord
from snowfall.vendor.direct_ferries.models import quote


class OfferDetails(RedisRecord):
    quote: quote.Quote
    round_trip_offer_cache_keys: Sequence[str] = []
    redis_key: str | None


class OffersCache(RedisRepository[OfferDetails]):
    _record_type: type[OfferDetails] = OfferDetails


class QuoteCache(RedisRepository[OfferDetails]):
    _record_type: type[OfferDetails] = OfferDetails
