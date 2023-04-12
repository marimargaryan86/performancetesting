import datetime
from typing import List, Type

from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetailsPassenger(RedisRecord):
    identifier: str
    passenger_type: str | None


class OfferDetails(RedisRecord):
    offer_id: str
    passengers: List[OfferDetailsPassenger]
    total_amount: str
    currency: str
    doc_required: bool = False
    last_travel_date: datetime.date


class OfferCache(RedisRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: Type[OfferDetails] = OfferDetails
