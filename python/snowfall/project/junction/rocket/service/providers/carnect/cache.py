import datetime

from snowfall.project.junction.rocket.service.providers.carnect import criteria
from snowfall.stdlib import string
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class Coordinates(RedisRecord):
    latitude: float
    longitude: float


class CarRentalResultDetail(RedisRecord):
    origin: Coordinates
    destination: Coordinates
    departure_at: datetime.datetime
    arrival_at: datetime.datetime
    driver_age: int
    model: str
    seats_count: int
    doors_count: int
    transmission: str
    baggage_quantity: int
    vehicle_type: str
    vendor_name: str | None
    vendor_code: str | None


class SearchResultCache(RedisRepository[CarRentalResultDetail]):
    """Stores search result in the cache."""

    _record_type: type[CarRentalResultDetail] = CarRentalResultDetail


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
                str(search.driver_age),
                str(search.pickup_datetime),
                str(search.return_datetime),
            ),
        ),
    )
