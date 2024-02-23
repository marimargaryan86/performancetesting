import asyncio
import logging
from collections.abc import Sequence
from datetime import date, datetime
from typing import Any

import allure
import pytest
from pymongo import MongoClient

from snowfall.project.junction.api_automation.conftest import (
    ConfigurationManager,
)
from snowfall.project.junction.api_automation.test_functions.benerail import (
    br_dialogues,
    br_passengers,
    br_trip_collections,
    get_br_id,
)
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


async def create_trip_candidates_search(
    mobile_hub_client: MobileApiClient,
    departure_after: datetime,
    origin: tuple[float, float],
    destination: tuple[float, float],
    passengers_dates_of_birth: Sequence[date],
    maximum_connections: Any,
    allowed_segment_types: Any,
) -> dict[str, Any]:
    return await mobile_hub_client.create_trip_candidates_search(
        origin,
        destination,
        departure_after,
        passengers_dates_of_birth,
        maximum_connections,
        allowed_segment_types,
    )


async def get_trip_candidate_list(
    mobile_hub_client: MobileApiClient,
    trip_candidate_id: str,
) -> dict[str, Any]:
    return await wait_for_response(
        lambda: mobile_hub_client.list_trip_candidates_offers(
            trip_candidate_search_id=trip_candidate_id,
        ),
        "No offers with the trip candidate",
    )


places_pairs = get_places()


@pytest.mark.manually()
@pytest.mark.parametrize("places_pairs", places_pairs)
async def test_rails_flow(  # noqa: WPS217, WPS218
    mongo_client: MongoClient[Any],
    mobile_hub_client: MobileApiClient,
    config_manager: ConfigurationManager,
    places_pairs: Sequence[tuple[Any, Any]],
    departure_after: datetime,
) -> None:
    origin_cord, destination_cord = await get_coordinates_by_place_name(
        mongo_client,
        places_pairs,
    )
    assert origin_cord, "Origin not found"
    assert destination_cord, "Destination not found"
    trip_candidate_resp = await wait_for_response(
        lambda: create_trip_candidates_search(
            mobile_hub_client,
            departure_after,
            origin_cord,
            destination_cord,
            [date(1980, 2, 3)],
            maximum_connections=2,
            allowed_segment_types=[LegType.rail],
        ),
        "Timeout reached with no trip candidate found.",
    )
    trip_candidate_id = trip_candidate_resp["data"]["id"]
    assert trip_candidate_id, "Trip candidate not found"
    await asyncio.sleep(90)
    offers_list_resp = await get_trip_candidate_list(
        mobile_hub_client,
        trip_candidate_id,
    )
    offer_data = offers_list_resp["data"]

    assert offer_data, "Empty offer list from trip candidate"
    assert offers_list_resp["included"], "trip candidate doesn't return any offer"
    offer_list_included = offers_list_resp["included"]
    assert offer_list_included, "Offers not found for the trip candidate"
    br_ids = await get_br_id(offer_list_included)

    assert br_ids[0], "Benerail ids not found"
    offer_count = br_ids[1]
    with allure.step("Step to log the offer count of trip candidate"):
        allure.attach(
            "OnD id for BR: {0}".format(br_ids[0]),
            "Offer Count from trip candidate : {0}".format(offer_count),
            "text/plain",
        )
    await asyncio.sleep(10)
    dialogues = await br_dialogues(config_manager)
    assert dialogues, "the dialogues of BR is empty"
    dialogues_id = dialogues[0]["result"]["id"]
    dialogue_etag = dialogues[1].get("ETag")
    await asyncio.sleep(20)
    passengers = await br_passengers(config_manager, dialogues_id, dialogue_etag)
    passenger_ids = passengers[0]["result"]["id"]
    dialogue_etag = passengers[1].get("ETag")
    assert passengers
    trip_filter_list_count = await br_trip_collections(
        config_manager,
        dialogues_id,
        dialogue_etag,
        br_ids[0],
        passenger_ids,
        str(departure_after),
    )

    with allure.step("Step to log the offer count of BR"):
        allure.attach(
            "Offer Count from BR: {0}".format(trip_filter_list_count),
            "text/plain",
        )
