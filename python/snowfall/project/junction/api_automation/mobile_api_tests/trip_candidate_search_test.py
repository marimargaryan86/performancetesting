import json
import logging
from datetime import date, datetime, timezone

import pytest

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.vendor.junction.go.client import LegType

ORIGIN = (48.8534951, 2.3483915)
DESTINATION = (51.5073219, -0.1276474)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


async def create_trip_candidate_search(
    mobile_client: MobileApiClient,
    departure_after: str,
) -> str:
    r1 = await mobile_client.create_trip_candidates_search(
        origin=ORIGIN,
        destination=DESTINATION,
        departure_after=datetime.fromisoformat(
            departure_after[:-1],
        ).astimezone(timezone.utc),
        allowed_segment_types=[LegType.air],
        passengers_dates_of_birth=[date(year=1980, month=2, day=3)],
        maximum_connections=2,
    )
    logger.info("create_candidate_trip_search response: %s", json.dumps(r1, indent=4))

    return r1["data"]["id"]


async def get_trip_candidate_search_by_id(
    mobile_client: MobileApiClient,
    departure_after: str,
) -> str:
    trip_search_id = await create_trip_candidate_search(
        mobile_client,
        departure_after,
    )
    r2 = await mobile_client.get_trip_candidate_search(trip_search_id)
    logger.info("get_trip_candidate_search_by_id: %s", json.dumps(r2, indent=4))

    return r2["data"]["id"]


@pytest.mark.integration()
async def test_list_trips_candidates_offers(
    mobile_client: MobileApiClient,
    departure_after: str,
) -> None:
    candidate_search = await get_trip_candidate_search_by_id(
        mobile_client,
        departure_after,
    )
    r3 = await mobile_client.list_trip_candidates_offers(candidate_search)
    logger.info("test_list_trips_candidates_offers: %s", json.dumps(r3, indent=4))

    assert r3["data"]
