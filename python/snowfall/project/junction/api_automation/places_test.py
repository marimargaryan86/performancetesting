import logging
from pprint import pformat
from typing import Any

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_places(
    host: str,
    api_token: str,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    client = JunctionClient(api_url="https://{0}".format(host), token=api_token)

    r1 = await return_list_places(client)
    assert is_valid_uuid(r1["data"][0]["id"], 5) is True, "no place returned!"


@pytest.mark.integration
async def test_places_place_id(
    host: str,
    api_token: str,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    client = JunctionClient(api_url="https://{0}".format(host), token=api_token)

    r0 = await return_list_places(client)
    assert is_valid_uuid(r0["data"][0]["id"], 5) is True, "no place returned!"

    r1 = await client.list_places()
    logging.info("list_places %s", pformat(r1))
    place_id = r1["data"][0]["id"]

    assert is_valid_uuid(place_id, 5) is not None, "place_id should be returned"

    r2 = await client.get_place_by_id(place_id)
    logging.info("get_place_by_id: %s", pformat(r2))


async def return_list_places(
    client: JunctionClient,
) -> dict[str, Any]:
    r1 = await client.list_places()
    logging.info("list_places %s", pformat(r1))
    return r1
