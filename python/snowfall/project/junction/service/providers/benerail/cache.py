from collections.abc import Mapping

from snowfall.project.junction.service.providers.benerail import criteria
from snowfall.stdlib import money, string
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetails(RedisRecord):
    offer_id: str
    price: str
    currency: money.Currency
    dialogue_id: str
    session_token: str | None = None
    passenger_etags: Mapping[str, str]
    departure_at: str


class OffersCache(RedisRepository[OfferDetails]):
    """Stores offer details in cache."""

    _record_type: type[OfferDetails] = OfferDetails


def generate_cache_key(
    search_criteria: criteria.SearchCriteria,
) -> str:
    return string.to_uuid(
        "\x00".join(
            (
                str(search_criteria.origin),
                str(search_criteria.destination),
                str(search_criteria.outbound_departure_datetime),
                *[str(dob) for dob in search_criteria.passenger_dobs],
            ),
        ),
    )
