import datetime
from typing import Type

from snowfall.stdlib import money
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetails(RedisRecord):
    expires_at: datetime.datetime
    price: str
    currency: money.Currency


class OfferCache(RedisRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: Type[OfferDetails] = OfferDetails
