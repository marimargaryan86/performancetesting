import json
import logging
from typing import Sequence

import pytest

from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_journey_by_id(client: JunctionClient) -> None:
    journey_ids = await return_journey_ids(client)

    for journey_id in journey_ids:
        r1 = await client.get_journey_by_id(journey_id)
        logging.info("get_journey_by_id: %s", json.dumps(r1, indent=4))
        assert r1


async def return_journey_ids(client: JunctionClient) -> Sequence[str]:
    r0 = await client.get_journeys()
    logging.info("get_journeys: %s", json.dumps(r0, indent=4))
    journey_ids = []
    journeys_data = r0["data"]
    for idx, _ in enumerate(journeys_data):
        journey_ids.append(journeys_data[idx]["id"])
    return journey_ids
