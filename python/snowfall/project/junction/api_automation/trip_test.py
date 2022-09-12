import logging
import time
from datetime import datetime, timezone
from pprint import pformat

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.junction.client import JunctionClient, LegType

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_trip_e2e_basic(
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

    r2 = await client.get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id response: %s", pformat(r2))

    trip_id = r2["data"][0]["id"]
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"


@pytest.mark.integration
async def test_get_trip_search_by_id(
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

    r2 = await client.get_trip_search_by_id(trip_search_id)
    logging.info("get_trip_search_by_id response: %s", pformat(r2))

    trip_id = r2["data"]["id"]
    assert is_valid_uuid(trip_id, 4) is True, "trip_id uuid must be in uuid v5 format"


@pytest.mark.integration
async def test_get_trips_by_trip_search_id(
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

    r2 = await client.get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id response: %s", pformat(r2))

    trip_id = r2["data"][0]["id"]
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"


@pytest.mark.integration
async def test_get_trip_by_id(
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

    r2 = await client.get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id response: %s", pformat(r2))

    trip_id = r2["data"][0]["id"]
    logging.info("trip_id: %s", trip_id)
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"

    time.sleep(15)
    r3 = await client.get_trip_by_id(trip_id)
    logging.info("get_trip_by_id: %s", pformat(r3))


async def return_trip_search_id(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> str:
    r1 = await client.create_trip_search(
        origin_id=origin,
        destination_id=destination,
        departure_after=datetime.fromisoformat(
            departure_after[:-1],
        ).astimezone(timezone.utc),
        leg_types=[LegType.air],
    )
    logging.info("create_trip_search response: %s", pformat(r1))

    return r1["data"]["id"]
