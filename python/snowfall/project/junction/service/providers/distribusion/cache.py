from typing import Type

from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetails(RedisRecord):
    fare_class: str


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in cache."""

    _record_type: Type[OfferDetails] = OfferDetails
