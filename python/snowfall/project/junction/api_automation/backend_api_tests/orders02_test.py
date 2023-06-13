import json
import logging
from collections.abc import Sequence

import pytest

from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_get_order_by_journey(
    junction_client: Client,
) -> None:
    journey_ids = await return_some_journey_ids(junction_client)
    assert journey_ids, "No journeys"

    was_any_order = False
    for journey_id in journey_ids:
        r1 = await junction_client.get_orders_by_journey_id(journey_id, limit=5)
        logging.info("get_journey_by_id: %s", json.dumps(r1, indent=4))
        was_any_order = was_any_order or bool(r1["data"])
        if was_any_order:
            break
    assert was_any_order, "No orders ever found"


async def return_some_journey_ids(junction_client: Client) -> Sequence[str]:
    r0 = await junction_client.get_journeys(limit=5)
    logging.info("get_order_by_journey: %s", json.dumps(r0, indent=4))
    journey_ids = []
    for journey in r0["data"]:
        journey_ids.append(journey["id"])
    return journey_ids
