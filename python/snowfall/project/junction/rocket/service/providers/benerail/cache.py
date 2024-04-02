import dataclasses
import datetime
from collections.abc import Sequence

from snowfall.project.junction.rocket.service.providers.benerail import (
    helper_models,
)
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetails(RedisRecord):
    passengers_dobs: Sequence[datetime.date]
    origin_station: str
    destination_station: str
    dialogue_id: str
    trip_filter_id: str
    outward_passengers_info: Sequence[helper_models.PassengerInfo]
    outbound_departure_datetime: datetime.datetime
    trip_id: str
    outward_offer_id: str
    comfort_class_value: str
    flexibility_value: str


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in cache."""

    _record_type: type[OfferDetails] = OfferDetails


@dataclasses.dataclass(frozen=True)
class Cache(object):
    offers_cache: OffersCache
