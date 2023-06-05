import asyncio
import json
import logging
from datetime import datetime, timezone

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.vendor.junction.go.client import LegType


@pytest.mark.integration()
async def test_trip_e2e_basic(
    host: str,
    protocol: str,
    mobile_client: MobileApiClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_search_id = await return_trip_search_id(
        mobile_client,
        departure_after,
        destination,
        origin,
    )
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    await asyncio.sleep(5)

    r2 = await mobile_client.trips().get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id response: %s", json.dumps(r2, indent=4))

    trip_id = r2["data"][0]["id"]
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"

    for link in r2["links"]:
        assert link.startswith(
            "{protocol}://{host}".format(protocol=protocol, host=host),
        ), "Link host is incorrect: {link} instead of {protocol}://{host}".format(
            link=link,
            protocol=protocol,
            host=host,
        )


@pytest.mark.integration()
async def test_get_trips_by_trip_search_id(
    mobile_client: MobileApiClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_search_id = await return_trip_search_id(
        mobile_client,
        departure_after,
        destination,
        origin,
    )
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    await asyncio.sleep(5)

    r2 = await mobile_client.trips().get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id response: %s", json.dumps(r2, indent=4))

    trip_id = r2["data"][0]["id"]
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"


@pytest.mark.integration()
async def test_get_trip_by_id(
    mobile_client: MobileApiClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_search_id = await return_trip_search_id(
        mobile_client,
        departure_after,
        destination,
        origin,
    )
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    await asyncio.sleep(5)

    r2 = await mobile_client.trips().get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id response: %s", json.dumps(r2, indent=4))

    trip_id = r2["data"][0]["id"]
    logging.info("trip_id: %s", trip_id)
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"

    await asyncio.sleep(15)
    r3 = await mobile_client.trips().get_trip_by_id(trip_id)
    logging.info("get_trip_by_id: %s", json.dumps(r3, indent=4))


@pytest.mark.integration()
async def test_get_legs_by_trip_id(
    mobile_client: MobileApiClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_search_id = await return_trip_search_id(
        mobile_client,
        departure_after,
        destination,
        origin,
    )
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    await asyncio.sleep(5)

    r2 = await mobile_client.trips().get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id response: %s", json.dumps(r2, indent=4))

    trip_id = r2["data"][0]["id"]
    logging.info("trip_id: %s", trip_id)
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"

    await asyncio.sleep(15)
    r3 = await mobile_client.legs().get_legs_by_trip_id(trip_id)
    logging.info("get_trip_by_id: %s", json.dumps(r3, indent=4))


@pytest.mark.integration()
async def test_get_legs_by_trip_search_id(
    mobile_client: MobileApiClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_search_id = await return_trip_search_id(
        mobile_client,
        departure_after,
        destination,
        origin,
    )
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    await asyncio.sleep(5)

    response = await mobile_client.legs().get_legs_by_trip_search_id(trip_search_id)
    logging.info("get_legs_by_trip_search_id: %s", json.dumps(response, indent=4))
    assert response


@pytest.mark.integration()
async def test_list_segments_by_trip(
    host: str,
    mobile_client: MobileApiClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_search_id = await return_trip_search_id(
        mobile_client,
        departure_after,
        destination,
        origin,
    )

    await asyncio.sleep(5)

    r2 = await mobile_client.trips().get_trips_by_trip_search_id(trip_search_id)

    logging.info("get_trips_by_trip_search_id response: %s", json.dumps(r2, indent=4))

    r3 = (
        await mobile_client.segments().get_segments_by_trip(
            r2["data"][0]["id"],
        ),
    )

    logging.info("get_segments_by_trip: %s", json.dumps(r3, indent=4))

    data_input = r3[0]["data"]
    logging.info("data_input: %s", data_input)
    for idx, _ in enumerate(data_input):
        assert data_input[idx]["id"] is not None
        assert data_input[idx]["type"] == "segments"
        assert bool(data_input[idx]["attributes"]) is False
        assert data_input[idx]["relationships"]["legs"]["data"] is not None
        assert data_input[idx]["links"] == {
            "self": "https://{0}/segments/{1}".format(
                host,
                data_input[idx]["id"],
            ),
        }


@pytest.mark.integration()
async def test_get_segments_by_trip_search_id(
    mobile_client: MobileApiClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_search_id = await return_trip_search_id(
        mobile_client,
        departure_after,
        destination,
        origin,
    )
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    await asyncio.sleep(5)

    response = await mobile_client.segments().get_segments_by_trip_search(
        trip_search_id,
    )
    logging.info("get_segments_by_trip_search: %s", json.dumps(response, indent=4))
    assert response


async def return_trip_search_id(
    mobile_client: MobileApiClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> str:
    r1 = await mobile_client.trips().create_trip_search(
        origin_id=origin,
        destination_id=destination,
        departure_after=datetime.fromisoformat(
            departure_after[:-1],
        ).astimezone(timezone.utc),
        allowed_segment_types=[LegType.air],
    )
    logging.info("create_trip_search response: %s", json.dumps(r1, indent=4))

    return r1["data"]["id"]
