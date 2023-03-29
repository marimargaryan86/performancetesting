import json
import logging

import pytest

from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_journeys(
    junction_client: Client,
) -> None:
    response = await junction_client.get_journeys()
    logging.info("get_journeys: %s", json.dumps(response, indent=4))
    assert response
