from typing import Sequence

import pytest

from snowfall.project.junction.api_automation.bookings01_test import (
    return_some_order_ids,
)
from snowfall.project.junction.api_automation.bookings02_test import (
    return_booking_ids_by_order_ids,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import with_log
from snowfall.vendor.junction.client import JunctionClient


@pytest.mark.integration
async def test_booking_details_by_booking_details_id(
    client: JunctionClient,
) -> None:
    detail_ids = await return_some_details_ids(client)
    assert detail_ids, "No details"

    was_any_details = False
    for detail_id in detail_ids:
        resp = await with_log(client.get_booking_details_by_id)(detail_id)
        was_any_details = was_any_details or bool(resp["data"])
        if was_any_details:
            break
    assert was_any_details, "No bookings details ever found"


async def return_some_details_ids(  # noqa: WPS210
    client: JunctionClient,
) -> Sequence[str]:
    order_ids = await return_some_order_ids(client)
    assert order_ids, "No orders"

    booking_ids = await return_booking_ids_by_order_ids(client, order_ids)
    assert booking_ids, "No bookings ever found"
    details_ids = []
    for booking_id in booking_ids:
        r0 = await with_log(client.get_booking_details_by_booking_id)(booking_id)

        for detail in r0["data"]:
            details_ids.append(detail["id"])
            if len(details_ids) >= 5:
                break
    return details_ids
