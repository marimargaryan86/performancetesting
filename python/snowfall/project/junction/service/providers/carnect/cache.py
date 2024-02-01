import datetime

from snowfall.project.junction.service.providers.carnect.v1 import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.redis import repository as redis_repository


class Coordinates(redis_repository.RedisRecord):
    latitude: float
    longitude: float


class OfferDetails(redis_repository.RedisRecord):
    departure_at: datetime.datetime
    arrival_at: datetime.datetime
    passengers_count: int
    origin: Coordinates
    destination: Coordinates


class OffersCache(redis_repository.PydanticRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: type[OfferDetails] = OfferDetails


def generate_cache_key(
    search_criteria: amqp_pb2.Criteria,
) -> str:
    return string.to_uuid(
        "\x00".join(
            (
                str(search_criteria.origin),
                str(search_criteria.destination),
                str(search_criteria.passengers_count),
                str(search_criteria.pick_up_datetime),
                str(search_criteria.return_datetime),
            ),
        ),
    )
