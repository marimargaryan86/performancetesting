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


class CarRentalResultDetails(RedisRecord):
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
    vendor: str | None


class SearchResultCache(RedisRepository[CarRentalResultDetails]):
    """Stores search result in the cache."""

    _record_type: type[CarRentalResultDetails] = CarRentalResultDetails


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
