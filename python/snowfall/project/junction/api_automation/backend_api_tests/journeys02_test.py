import json
import logging
from collections.abc import Sequence

import pytest

from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_get_journey_by_id(junction_client: Client) -> None:
    journey_ids = await return_journey_ids(junction_client)

    for journey_id in journey_ids:
        r1 = await junction_client.get_journey_by_id(journey_id)
        logging.info("get_journey_by_id: %s", json.dumps(r1, indent=4))
        assert r1


async def return_journey_ids(junction_client: Client) -> Sequence[str]:
    r0 = await junction_client.get_journeys()
    logging.info("get_journeys: %s", json.dumps(r0, indent=4))
    journeys_data = r0["data"]

    return [journey["id"] for journey in journeys_data]
