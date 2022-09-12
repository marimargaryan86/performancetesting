import logging
import time
from pprint import pformat

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.trip_test import return_trip_search_id
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_segment_by_id(
    host: str,
    api_token: str,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    client = JunctionClient(api_url="https://{0}".format(host), token=api_token)

    trip_search_id = await return_trip_search_id(
        client,
        departure_after,
        destination,
        origin,
    )
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    time.sleep(5)

    segment_id = await return_segment_id_from_trip_search_id(client, trip_search_id)

    logging.info("segment_id: %s", segment_id)
    assert (
        is_valid_uuid(segment_id, 5) is True
    ), "segment_id uuid must be in uuid v5 format"

    r3 = await client.get_segment_by_id(segment_id)
    logging.info("get_segment_by_id: %s", pformat(r3, indent=2))

    assert r3["data"]["id"] == segment_id, "segment_id should match"


@pytest.mark.integration
async def test_get_legs_by_segment_id(
    host: str,
    api_token: str,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    client = JunctionClient(api_url="https://{0}".format(host), token=api_token)

    trip_search_id = await return_trip_search_id(
        client,
        departure_after,
        destination,
        origin,
    )
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    time.sleep(5)

    segment_id = await return_segment_id_from_trip_search_id(client, trip_search_id)

    r1 = await client.get_legs_by_segment_id(
        segment_id,
    )
    logging.info("get_legs_by_segment_id: %s", pformat(r1))
    assert (
        is_valid_uuid(r1["data"][0]["id"], 5) is True
    ), "trip_search_id uuid in v4 format"


async def return_segment_id_from_trip_search_id(
    client: JunctionClient,
    trip_search_id: str,
) -> str:
    r2 = await client.get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id response: %s", pformat(r2))
    relationships = r2["data"][0]["relationships"]

    return relationships["segments"]["data"][0]["id"]
