import datetime
from typing import Type

from snowfall.stdlib import money
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetails(RedisRecord):
    quote_id: str
    expires_at: datetime.datetime
    price: str
    currency: money.Currency


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: Type[OfferDetails] = OfferDetails
