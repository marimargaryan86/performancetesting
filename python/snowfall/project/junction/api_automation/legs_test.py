import logging
import time
from pprint import pformat
from typing import Any

import pytest

from snowfall.project.junction.api_automation.segments_test import (
    return_segment_id_from_trip_search_id,
)
from snowfall.project.junction.api_automation.trip_test import return_trip_search_id
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_leg_by_id(
    host: str,
    api_token: str,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    client = JunctionClient(api_url="https://{0}".format(host), token=api_token)

    r3 = await return_get_segment_by_id_response(
        client,
        departure_after,
        destination,
        origin,
    )
    relationships = r3["data"]["relationships"]

    r4 = await client.get_leg_by_id(
        leg_id=relationships["legs"]["data"][0]["id"],
    )
    logging.info("get_leg_by_id: %s", pformat(r4))

    leg_id = r4["data"]["id"]
    assert leg_id == relationships["legs"]["data"][0]["id"], "leg_id should match"


async def return_get_segment_by_id_response(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> dict[str, Any]:
    trip_search_id = await return_trip_search_id(
        client,
        departure_after,
        destination,
        origin,
    )
    time.sleep(5)
    r3 = await client.get_segment_by_id(
        await return_segment_id_from_trip_search_id(
            client,
            trip_search_id,
        ),
    )
    logging.info("get_segment_by_id: %s", pformat(r3, indent=2))
    return r3
