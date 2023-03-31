import json
import logging
from typing import Any

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_places(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    r1 = await return_list_places(junction_client)
    assert is_valid_uuid(r1["data"][0]["id"], 5) is True, "no place returned!"


@pytest.mark.integration()
async def test_places_place_id(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    r0 = await return_list_places(junction_client)
    assert is_valid_uuid(r0["data"][0]["id"], 5) is True, "no place returned!"

    r1 = await junction_client.places().list_places()
    logging.info("list_places %s", json.dumps(r1, indent=4))
    place_id = r1["data"][0]["id"]

    assert is_valid_uuid(place_id, 5) is not None, "place_id should be returned"

    r2 = await junction_client.places().get_place_by_id(place_id)
    logging.info("get_place_by_id: %s", json.dumps(r2, indent=4))


@pytest.mark.integration()
async def test_get_places_types(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    response = await junction_client.places().get_places_types()
    logging.info("get_places_types: %s", json.dumps(response, indent=4))

    for data_item in response["data"]:
        assert data_item["id"] is not None
        assert data_item["type"] == "place-types"
        assert data_item["attributes"] == {"name": data_item["id"]}
        assert "https" in data_item["links"]["self"]


@pytest.mark.integration()
async def test_get_places_type(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    response_places = await junction_client.places().get_places_types()

    places_ids = []
    for data_item in response_places["data"]:
        places_ids.append(data_item["id"])

    for places_id in places_ids:
        response_place = await junction_client.places().get_places_type(places_id)

        logging.info("get_places_type: %s", json.dumps(response_place, indent=4))

        assert response_place["data"]["id"] is not None
        assert response_place["data"]["type"] == "place-types"
        assert response_place["data"]["attributes"] == {
            "name": response_place["data"]["id"],
        }
        assert "https" in response_place["data"]["links"]["self"]


async def return_list_places(
    junction_client: Client,
) -> dict[str, Any]:
    r1 = await junction_client.places().list_places()
    logging.info("list_places %s", json.dumps(r1, indent=4))
    return r1
