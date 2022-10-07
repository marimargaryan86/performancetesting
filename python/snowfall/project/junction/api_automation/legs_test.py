import json
import logging
import time
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
    client: JunctionClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
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
    logging.info("get_leg_by_id: %s", json.dumps(r4, indent=4))

    leg_id = r4["data"]["id"]
    assert leg_id == relationships["legs"]["data"][0]["id"], "leg_id should match"


@pytest.mark.integration
async def test_get_leg_types(
    client: JunctionClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    response = await client.get_legs_types()
    logging.info("get_legs_types: %s", json.dumps(response, indent=4))
    assert response["data"][0]["id"] == "unspecified"
    assert response["data"][1]["id"] == "air"
    assert response["data"][2]["id"] == "rail"


@pytest.mark.integration
async def test_get_leg_type_by_id(
    client: JunctionClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    leg_types = await return_leg_types(client)

    for leg_type in leg_types:
        r1 = await client.get_leg_type_by_id(leg_type)
        logging.info("get_leg_type_by_id: %s", json.dumps(r1, indent=4))
        assert r1["data"]["id"] in leg_types


async def return_leg_types(client: JunctionClient) -> list[str]:
    r0 = await client.get_legs_types()
    logging.info("get_legs_types: %s", json.dumps(r0, indent=4))
    leg_types = []
    for idx, _ in enumerate(r0["data"]):
        leg_types.append(r0["data"][idx]["id"])
    logging.info("leg_types: %s", leg_types)
    return leg_types


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
    logging.info("get_segment_by_id: %s", json.dumps(r3, indent=4))
    return r3
