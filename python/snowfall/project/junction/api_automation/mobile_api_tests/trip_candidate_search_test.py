import asyncio
import json
import logging
from datetime import UTC, date, datetime

import pytest

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.vendor.junction.go.client import LegType

ORIGIN = (51.5073219, -0.1276474)
DESTINATION = (52.3727598, 4.8936041)


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
            departure_after,
        ).astimezone(UTC),
        allowed_segment_types=[LegType.air],
        passengers_dates_of_birth=[date(year=1980, month=2, day=3)],
        maximum_connections=1,
    )
    logger.info("create_trip_candidates_search: %s", json.dumps(r1, indent=4))

    trip_search_id = r1["data"]["id"]
    for _ in range(500):
        await asyncio.sleep(3)
        r2 = await mobile_client.get_trip_candidate_search(trip_search_id)
        status = r2["data"]["attributes"]["status"]
        logger.info("create_trip_candidates_search: GET status: %s", status)
        if status == "completed":
            break
    else:
        raise AssertionError("Timed out")

    return trip_search_id


@pytest.mark.skip(reason="temporary skipped")
async def test_list_trips_candidates_offers(
    mobile_client: MobileApiClient,
    departure_after: str,
) -> None:
    candidate_search = await create_trip_candidate_search(
        mobile_client,
        departure_after,
    )
    r3 = await mobile_client.list_trip_candidates_offers(candidate_search)
    logger.info("test_list_trips_candidates_offers: %s", json.dumps(r3, indent=4))

    assert r3["data"][0]["id"] is not None
