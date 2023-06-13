import json
import logging
from collections.abc import Sequence

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.bookings01_test import (
    return_some_order_ids,
)
from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_get_booking_by_booking_id(
    junction_client: Client,
) -> None:
    order_ids = await return_some_order_ids(junction_client)
    assert order_ids, "No orders"

    booking_ids = await return_booking_ids_by_order_ids(junction_client, order_ids)
    assert booking_ids, "No bookings ever found"

    was_any_booking = False
    for booking_id in booking_ids:
        resp = await junction_client.get_booking_by_id(booking_id)
        logging.info(
            "get_booking_by_booking_id: %s",
            json.dumps(resp, indent=4),
        )
        was_any_booking = was_any_booking or bool(resp["data"])
        if was_any_booking:
            break
    assert was_any_booking, "No details"


async def return_booking_ids_by_order_ids(
    junction_client: Client,
    order_ids: Sequence[str],
) -> Sequence[str]:
    booking_ids = []
    for order_id in order_ids:
        resp = await junction_client.get_bookings_by_order_id(order_id)
        logging.info("get_bookings_by_order_id: %s", json.dumps(resp, indent=4))
        for booking in resp["data"]:
            booking_ids.append(booking["id"])
            if len(booking_ids) >= 5:
                break
    return booking_ids
