import datetime

from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetailsPassenger(RedisRecord):
    identifier: str
    passenger_type: str | None


class OfferDetails(RedisRecord):
    offer_id: str
    passengers: list[OfferDetailsPassenger]
    total_amount: str
    currency: str
    doc_required: bool = False
    last_travel_date: datetime.date


class OfferCache(RedisRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: type[OfferDetails] = OfferDetails
