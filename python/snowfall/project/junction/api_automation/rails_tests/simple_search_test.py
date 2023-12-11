import asyncio
import logging
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

import allure
import pytest
from pymongo import MongoClient

from snowfall.project.junction.api_automation.test_functions.helper import (
    get_coordinates_by_place_name,
    get_places,
    wait_for_response,
)
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.vendor.junction.go.client import LegType

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


async def create_offer_simple_search(
    mobile_hub_client: MobileApiClient,
    departure_after: datetime,
    origin: tuple[float, float],
    destination: tuple[float, float],
    passengers_dates_of_birth: Sequence[date],
    maximum_connections: Any,
    allowed_segment_types: Any,
) -> dict[str, Any]:
    return await mobile_hub_client.create_offer_simple_search(
        origin,
        destination,
        departure_after,
        passengers_dates_of_birth,
        maximum_connections,
        allowed_segment_types,
    )


async def get_offer_list_simple_search(
    mobile_hub_client: MobileApiClient,
    offer_id_simple_search: str,
) -> dict[str, Any]:
    return await wait_for_response(
        lambda: mobile_hub_client.list_offers_simple_search(
            offer_simple_search_id=offer_id_simple_search,
        ),
        "No offers with the simple search",
    )


async def get_offers_count_simple_search(
    offer_list: Mapping[str, Any],
) -> int:
    offer_data = offer_list["data"]
    assert offer_data, "Empty data in simple search response"
    assert offer_list["included"], "Simple Search doesn't return any offer"
    offer_list_included = offer_list["included"]
    offer_item_count = 0
    for offer_item in offer_list_included:
        if "type" in offer_item and offer_item["type"] == "trip-offer-group-details":
            offer_item_count += 1

    return offer_item_count


places_pairs = get_places()


@pytest.mark.manually()
@pytest.mark.parametrize("places_pairs", places_pairs)
async def test_rails_flow_simple_search(  # noqa: WPS217, WPS218
    mongo_client: MongoClient[Any],
    mobile_hub_client: MobileApiClient,
    places_pairs: Sequence[tuple[Any, Any]],
    departure_after: datetime,
) -> None:
    origin_cord, destination_cord = await get_coordinates_by_place_name(
        mongo_client,
        places_pairs,
    )

    assert origin_cord, "Origin not found"
    assert destination_cord, "Destination not found"
    await asyncio.sleep(10)
    offer_simple_search = await create_offer_simple_search(
        mobile_hub_client,
        departure_after,
        origin_cord,
        destination_cord,
        [date(1980, 2, 3)],
        maximum_connections=2,
        allowed_segment_types=[LegType.rail],
    )

    offer_id_simple_search = offer_simple_search["data"]["id"]
    assert offer_id_simple_search, "offer is with simpl search wasn't found"
    with allure.step("Step to log the current OnD coordinates"):
        allure.attach(
            "current OnD coordinates : {0}, {1}".format(origin_cord, destination_cord),
            "text/plain",
        )

    assert origin_cord, "Origin not found"
    assert destination_cord, "Destination not found"
    await asyncio.sleep(10)
    offer_simple_search = await create_offer_simple_search(
        mobile_hub_client,
        departure_after,
        origin_cord,
        destination_cord,
        [date(1980, 2, 3)],
        maximum_connections=2,
        allowed_segment_types=[LegType.rail],
    )

    offer_id_simple_search = offer_simple_search["data"]["id"]
    assert offer_id_simple_search, "offer is with simpl search wasn't found"

    offers_list = await get_offer_list_simple_search(
        mobile_hub_client,
        offer_id_simple_search,
    )
    offers_count = await get_offers_count_simple_search(offers_list)
    assert offers_count, "offers count by simple search"
    with allure.step("Step to log the offer count of simple search"):
        allure.attach(
            "Offer Count from simple search : {0}".format(offers_count),
            "text/plain",
        )
