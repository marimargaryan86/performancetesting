from typing import Type

from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OptionNotFoundError(Exception):
    """Raised when an offer is not found in the cache."""


class PriceQuoteNotFoundError(Exception):
    """Raised when a price quote is not found in the cache."""


class MockDetails(RedisRecord):
    amount: int
    currency: str


class OptionCache(RedisRepository[MockDetails]):
    """Stores options in the cache."""

    _record_type: Type[MockDetails] = MockDetails


class PriceQuoteCache(RedisRepository[MockDetails]):
    """Stores price quotes in the cache."""

    _record_type: Type[MockDetails] = MockDetails
