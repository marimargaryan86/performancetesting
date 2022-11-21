import json
import logging
import time
from typing import Sequence

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.offers01_test import (
    return_trip_offer_search_ids,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.junction import models
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_orders_status(
    client: JunctionClient,
    origin: str,
    departure_after: str,
    destination: str,
) -> None:
    trips_offer_search_ids = await return_trip_offer_search_ids(
        client,
        departure_after,
        destination,
        origin,
    )
    assert trips_offer_search_ids, "No searches"

    offer_ids = (await client.get_search_offer_ids(trips_offer_search_ids[0]))["data"]
    assert offer_ids, "No offers"

    offer_option_ids = await return_options_by_order_groups(client, offer_ids[0])

    order_id = await get_orders_id(
        client=client,
        offer_id=offer_ids[0],
        option_ids=offer_option_ids,
        passengers=[],
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

    time.sleep(5)


async def get_orders_id(
    client: JunctionClient,
    offer_id: str,
    option_ids: Sequence[str],
    passengers: Sequence[models.Passenger],
    contact_details: models.ContactDetails,
) -> str:
    r1 = await client.create_order(
        option_ids=option_ids,
        passengers=passengers,
        contact_details=contact_details,
        offer_id=offer_id,
    )
    order_id = r1["data"]["id"]
    logging.info("create_order_search: %s", json.dumps(r1, indent=4))
    return order_id


async def return_options_by_order_groups(
    client: JunctionClient,
    order_group_ids: Sequence[str],
) -> Sequence[str]:
    option_ids = []
    for group_id in order_group_ids:
        resp = await client.get_offer_options_by_offer_group_id(group_id)
        for option in resp["data"]:
            option_ids.append(option["id"])
    return option_ids
