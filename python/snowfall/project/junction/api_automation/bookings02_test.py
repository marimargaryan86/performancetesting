from typing import Sequence

import pytest

from snowfall.project.junction.api_automation.bookings01_test import (
    return_some_order_ids,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import with_log
from snowfall.vendor.junction.client import JunctionClient


@pytest.mark.integration
async def test_list_booking_details_by_booking_id(
    client: JunctionClient,
) -> None:
    order_ids = await return_some_order_ids(client)
    assert order_ids, "No orders"

    booking_ids = await return_booking_ids_by_order_ids(client, order_ids)
    assert booking_ids, "No bookings ever found"

    was_any_details = False
    for booking_id in booking_ids:
        resp = await with_log(client.get_booking_details_by_booking_id)(booking_id)
        was_any_details = was_any_details or bool(resp["data"])
        if was_any_details:
            break
    assert was_any_details, "No details"


async def return_booking_ids_by_order_ids(
    client: JunctionClient,
    order_ids: Sequence[str],
) -> Sequence[str]:
    booking_ids = []
    for order_id in order_ids:
        resp = await with_log(client.get_bookings_by_order_id)(order_id)
        for booking in resp["data"]:
            booking_ids.append(booking["id"])
            if len(booking_ids) >= 5:
                break
    return booking_ids
