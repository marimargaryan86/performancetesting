import datetime
from collections.abc import Sequence

from snowfall.project.junction.go.v1 import models_pb2 as go_models
from snowfall.project.junction.rocket.service.providers.silverrail import criteria
from snowfall.stdlib import string
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class QuoteNotFoundError(Exception):
    """Raised when quote is not found in the cache."""


class Coordinates(RedisRecord):
    latitude: float
    longitude: float


class RailResultDetail(RedisRecord):
    origin: str
    destination: str
    outbound_departure_after: datetime.datetime
    outbound_departure_before: datetime.datetime
    passenger_dobs: Sequence[datetime.date]
    cabin_class: go_models.CabinClass.Type.ValueType


class ResultDetailCache(RedisRepository[RailResultDetail]):
    """Stores search result in the cache."""

    _record_type: type[RailResultDetail] = RailResultDetail


class PriceQuote(RedisRecord):
    """Stores price quotes in the cache."""

    leg_solution: bytes
    ptp_price: bytes


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
