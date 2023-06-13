import json
import logging
from datetime import UTC, date, datetime

import pytest

from snowfall.vendor.junction.go.client import Client, LegType

ORIGIN = (51.47002, -0.454295)
DESTINATION = (37.937225, 23.945238)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


async def create_trip_candidate_search(
    junction_client: Client,
    departure_after: str,
    year: int,
    month: int,
    day: int,
    maximum_connections: int,
) -> str:
    r1 = await junction_client.trips().create_trip_candidates_search(
        origin=ORIGIN,
        destination=DESTINATION,
        departure_after=datetime.fromisoformat(
            departure_after[:-1],
        ).astimezone(UTC),
        allowed_segment_types=[LegType.air],
        passengers_dates_of_birth=[date(year=year, month=month, day=day)],
        maximum_connections=maximum_connections,
    )
    logging.info("create_candidate_trip_search response: %s", json.dumps(r1, indent=4))

    return r1["data"]["id"]


@pytest.mark.integration()
async def test_get_trip_candidate_search(
    junction_client: Client,
    departure_after: str,
) -> None:
    trip_id = await create_trip_candidate_search(
        junction_client,
        departure_after=departure_after,
        year=1992,
        month=4,
        day=29,
        maximum_connections=1,
    )
    assert trip_id is not None
