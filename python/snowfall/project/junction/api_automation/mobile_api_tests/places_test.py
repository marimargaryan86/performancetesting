import json
import logging

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.junction.client import JunctionClient


@pytest.mark.integration
async def test_places_place_id(
    client: JunctionClient,
) -> None:
    r1 = await client.places().list_places()
    logging.info("list_places %s", json.dumps(r1, indent=4))
    place_id = r1["data"][0]["id"]
    assert is_valid_uuid(place_id, 5) is True, "no place returned!"

    r2 = await client.places().get_place_by_id(place_id)
    logging.info("get_place_by_id: %s", json.dumps(r2, indent=4))
