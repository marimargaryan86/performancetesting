import json
import logging
from typing import Sequence

import pytest

from snowfall.project.junction.api_automation.mobile_api_tests.offers01_test import (
    return_trip_offer_search_ids,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.vendor.junction.go import models


@pytest.mark.integration()
async def test_get_orders_status(  # noqa: WPS210
    mobile_client: MobileApiClient,
    origin: str,
    departure_after: str,
    destination: str,
) -> None:
    trips_offer_search_ids = await return_trip_offer_search_ids(
        mobile_client,
        departure_after,
        destination,
        origin,
    )
    assert trips_offer_search_ids, "No searches"

    offer_ids = (await mobile_client.get_search_offer_ids(trips_offer_search_ids[0]))[
        "data"
    ]
    assert offer_ids, "No offers"

    offer_option_ids = await return_options_by_order_groups(mobile_client, offer_ids[0])

    resp = await mobile_client.create_payment(currency="EUR", amount="13.59")
    payment_id = resp["data"]["id"]

    order_id = await get_orders_id(
        mobile_client=mobile_client,
        offer_id=offer_ids[0],
        option_ids=offer_option_ids,
        passengers=[],
        payment_id=payment_id,
        contact_details=models.ContactDetails(
            email="example@example.com",
            phone_number="+48500600700",
            address=models.Address(
                address_lines=["Addr1"],
                country_code="PL",
                postal_code="95-000",
                city="Lodz",
            ),
        ),
    )
    assert is_valid_uuid(order_id) is True, "order_id uuid in v4 format"


async def get_orders_id(
    mobile_client: MobileApiClient,
    offer_id: str,
    option_ids: Sequence[str],
    passengers: Sequence[models.Passenger],
    contact_details: models.ContactDetails,
    payment_id: str,
) -> str:
    r1 = await mobile_client.create_order_with_payment(
        option_ids=option_ids,
        passengers=passengers,
        contact_details=contact_details,
        offer_id=offer_id,
        payment_id=payment_id,
    )
    order_id = r1["data"]["id"]
    logging.info("create_order_search: %s", json.dumps(r1, indent=4))
    return order_id


async def return_options_by_order_groups(
    mobile_client: MobileApiClient,
    order_group_ids: Sequence[str],
) -> Sequence[str]:
    option_ids = []
    for group_id in order_group_ids:
        resp = await mobile_client.get_offer_options_by_offer_group_id(group_id)
        for option in resp["data"]:
            option_ids.append(option["id"])
    return option_ids
