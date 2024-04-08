from snowfall.project.junction.rocket.service.providers.silverrail import criteria
from snowfall.stdlib import string
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class Coordinates(RedisRecord):
    latitude: float
    longitude: float


class RailResultDetail(RedisRecord):
    origin: Coordinates
    destination: Coordinates
    # TODO(regis.blanc): Add missing props


class SearchResultCache(RedisRepository[RailResultDetail]):
    """Stores search result in the cache."""

    _record_type: type[RailResultDetail] = RailResultDetail


class PriceQuote(RedisRecord):
    """Stores price quotes in the cache."""

    quote_id: str


class QuoteCache(RedisRepository[PriceQuote]):
    """Stores pricing details in the cache."""

    _record_type: type[PriceQuote] = PriceQuote


def generate_cache_key(search: criteria.Criteria) -> str:
    return string.to_uuid(
        "\x00".join(
            (
                str(search.origin),
                str(search.destination),
            ),
        ),
    )
