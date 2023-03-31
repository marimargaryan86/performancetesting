from typing import Sequence

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.bookings01_test import (
    return_some_order_ids,
)
from snowfall.project.junction.api_automation.backend_api_tests.bookings02_test import (
    return_booking_ids_by_order_ids,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import with_log
from snowfall.vendor.junction.go.client import Client


@pytest.mark.integration()
async def test_booking_details_by_booking_details_id(
    junction_client: Client,
) -> None:
    detail_ids = await return_some_details_ids(junction_client)
    assert detail_ids, "No details"

    was_any_details = False
    for detail_id in detail_ids:
        resp = await with_log(junction_client.get_booking_details_by_id)(detail_id)
        was_any_details = was_any_details or bool(resp["data"])
        if was_any_details:
            break
    assert was_any_details, "No bookings details ever found"


async def return_some_details_ids(  # noqa: WPS210
    junction_client: Client,
) -> Sequence[str]:
    order_ids = await return_some_order_ids(junction_client)
    assert order_ids, "No orders"

    booking_ids = await return_booking_ids_by_order_ids(junction_client, order_ids)
    assert booking_ids, "No bookings ever found"
    details_ids = []
    for booking_id in booking_ids:
        r0 = await with_log(junction_client.get_booking_details_by_booking_id)(
            booking_id,
        )

        for detail in r0["data"]:
            details_ids.append(detail["id"])
            if len(details_ids) >= 5:
                break
    return details_ids
