from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class SearchResultNotFoundError(Exception):
    """Raised when a search result is not found in the cache."""


class QuoteNotFoundError(Exception):
    """Raised when a quote is not found in the cache."""


class MockDetails(RedisRecord):
    amount: int
    currency: str


class SearchResultCache(RedisRepository[MockDetails]):
    """Stores search result in the cache."""

    _record_type: type[MockDetails] = MockDetails


class QuoteCache(RedisRepository[MockDetails]):
    """Stores price quotes in the cache."""

    _record_type: type[MockDetails] = MockDetails
