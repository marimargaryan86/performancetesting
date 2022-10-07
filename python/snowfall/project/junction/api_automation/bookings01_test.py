import json
import logging
from typing import Sequence

import pytest

from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_booking_by_id(
    client: JunctionClient,
) -> None:
    order_ids = await return_some_order_ids(client)
    assert order_ids, "No orders"

    was_any_booking = False
    for order_id in order_ids:
        resp = await client.get_bookings_by_order_id(order_id)
        logging.info("get_journey_by_id: %s", json.dumps(resp, indent=4))
        was_any_booking = was_any_booking or bool(resp["data"])
        if was_any_booking:
            break
    assert was_any_booking, "No bookings ever found"


async def return_some_order_ids(client: JunctionClient) -> Sequence[str]:
    r0 = await client.get_journeys(limit=5)
    logging.info("get_order_by_journey: %s", json.dumps(r0, indent=4))
    order_ids = []
    for journey in r0["data"]:
        for order in journey["relationships"]["orders"]["data"]:
            order_ids.append(order["id"])
    return order_ids
