import dataclasses
import datetime
from collections.abc import Sequence

from snowfall.project.junction.service.providers.benerail import criteria, helper_models
from snowfall.stdlib import money, string
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetails(RedisRecord):
    passengers_dobs: Sequence[datetime.date]
    origin_station: str
    destination_station: str
    outbound_departure_datetime: datetime.datetime
    trip_id: str
    comfort_class_value: str
    flexibility_value: str
    session_token: str | None = None


class BookingOfferDetails(RedisRecord):
    offer_id: str
    price: str
    currency: money.Currency
    dialogue_info: helper_models.DialogueInfo
    passengers_info: Sequence[helper_models.PassengerInfo]
    departure_at: str
    session_token: str | None = None


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in cache."""

    _record_type: type[OfferDetails] = OfferDetails


class BookingOffersCache(RedisRepository[BookingOfferDetails]):
    """Stores offer details in cache."""

    _record_type: type[BookingOfferDetails] = BookingOfferDetails


@dataclasses.dataclass(frozen=True)
class Cache(object):
    offers_cache: OffersCache
    booking_offers_cache: BookingOffersCache


def generate_cache_key(
    search_criteria: criteria.SearchCriteria,
) -> str:
    return string.to_uuid(
        "\x00".join(
            (
                str(search_criteria.origin),
                str(search_criteria.destination),
                str(search_criteria.outbound_departure_datetime),
                *[str(dob) for dob in sorted(search_criteria.passenger_dobs)],
            ),
        ),
    )
