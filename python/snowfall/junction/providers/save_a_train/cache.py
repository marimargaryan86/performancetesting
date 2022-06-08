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


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in cache."""

    _record_type: Type[OfferDetails] = OfferDetails
