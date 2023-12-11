import datetime

from snowfall.project.junction.service.providers.karhoo.v1 import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class Coordinates(RedisRecord):
    latitude: float
    longitude: float


class CabinClass(RedisRecord):
    type: int  # noqa: A003
    marketing_name: str


class OfferDetails(RedisRecord):
    # TODO: remove quote_id one orders is implemented.
    quote_id: str = ""
    departure_at: datetime.datetime
    price: str
    currency: money.Currency
    passengers_count: int
    origin: Coordinates
    destination: Coordinates
    cabin_class: CabinClass


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: type[OfferDetails] = OfferDetails


class PriceQuote(RedisRecord):
    quote_id: str
    quotes_response_id: str
    expires_at: datetime.datetime
    price: str
    currency: money.Currency


class PricingCache(RedisRepository[PriceQuote]):
    """Stores pricing details in the cache."""

    _record_type: type[PriceQuote] = PriceQuote


def generate_cache_key(
    search_criteria: amqp_pb2.Criteria,
) -> str:
    return string.to_uuid(
        "\x00".join(
            (
                str(search_criteria.origin),
                str(search_criteria.destination),
                str(search_criteria.passengers_count),
                str(search_criteria.departure_datetime),
            ),
        ),
    )
