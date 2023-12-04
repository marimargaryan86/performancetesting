import asyncio
import logging
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from typing import Any

import allure
import pytest
from pymongo import MongoClient

from snowfall.project.junction.api_automation.conftest import (
    ConfigurationManager,
    get_coordinates_by_place_name,
    get_places,
    make_br_request,
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


async def get_br_id(  # noqa: WPS231
    offer_list_included: Sequence[Any],
) -> tuple[list[dict[str, Any]], int]:
    offer_item_count = 0
    origin_destination_pairs = []
    trip_offer_group_ids = set()

    provider_id = "caefde65-c15c-4b60-b8d9-27638b50b08f"
    for offer_item in offer_list_included:
        if "type" in offer_item and offer_item["type"] == "trip-offer-group-details":
            offer_item_count += 1
        meta = offer_item.get("meta", {})
        details = offer_item.get("relationships", {}).get("details", {}).get("data", [])

        if meta.get("providerId") == provider_id:
            for detail in details:
                if detail.get("type") == "trip-offer-group-details":
                    trip_offer_group_ids.add(detail["id"])
    for group_id in trip_offer_group_ids:
        if offer_item.get("id") == group_id:
            legs = offer_item.get("attributes", {}).get("legs", [])
            for leg in legs:
                origin = leg.get("origin", {}).get("ref")
                destination = leg.get("destination", {}).get("ref")
                origin_destination_pairs.append(
                    {"origin": origin, "destination": destination},
                )

    return origin_destination_pairs, offer_item_count


async def br_dialogues(
    config_manager: ConfigurationManager,
) -> tuple[dict[str, Any], Any]:
    method = "POST"
    endpoint = "/dialogue-engine/dialogues"
    payload: dict[str, Any] = {}

    return await make_br_request(config_manager, method, endpoint, payload)


async def br_passengers(
    config_manager: ConfigurationManager,
    dialogues_id: str,
    dialogue_etag: str,
) -> tuple[dict[str, Any], Any]:
    method = "POST"
    endpoint = "/dialogue-engine/dialogues/{0}/passengers".format(dialogues_id)
    headers = {
        "If-Match": dialogue_etag,
    }
    payload = {
        "externalReference": None,
        "dateOfBirth": "1991-09-17",
        "cards": None,
        "corporateContracts": None,
        "gender": None,
        "details": {
            "preferredLanguage": None,
            "title": None,
            "firstName": "Mari",
            "lastName": "Margaryan",
            "email": "mari.m@snowfalltravel.com",
            "phoneNumber": None,
        },
    }
    return await make_br_request(config_manager, method, endpoint, payload, headers)


async def br_trip_filter(
    config_manager: ConfigurationManager,
    dialogues_id: str,
    dialogue_etag: str,
    departure_after: str,
    br_o_d: Mapping[str, str],
) -> tuple[dict[str, Any], Any]:
    method = "POST"
    endpoint = "/dialogue-engine/dialogues/{0}/trip-filters".format(dialogues_id)
    headers = {
        "If-Match": dialogue_etag,
    }
    departure_date_time_str = datetime.strptime(
        departure_after,
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ).replace(tzinfo=UTC)
    departure_date_time = departure_date_time_str.isoformat()

    origin_id = br_o_d.get("origin")
    destination_id = br_o_d.get("destination")

    payload = {
        "origin": origin_id,
        "destination": destination_id,
        "via": None,
        "trainTypes": None,
        "departureDateTime": departure_date_time,
        "params": None,
    }
    return await make_br_request(
        config_manager,
        method,
        endpoint,
        payload,
        headers,
    )


async def br_trip_offer_filter(
    config_manager: ConfigurationManager,
    dialogues_id: str,
    passenger_ids: str,
    dialogue_etag: str,
    trip_filter_id: str,
) -> tuple[dict[str, Any], Any]:
    method = "POST"
    endpoint = "/dialogue-engine/dialogues/{0}/trip-offer-filters".format(
        dialogues_id,
    )
    headers = {
        "If-Match": dialogue_etag,
    }
    payload = {
        "tripFilterId": trip_filter_id,
        "tripId": None,
        "passengers": [passenger_ids],
        "returnTripParams": None,
    }
    return await make_br_request(
        config_manager,
        method,
        endpoint,
        payload,
        headers,
    )


async def br_trip_offer_collection(
    config_manager: ConfigurationManager,
    dialogue_etag: str,
    trip_offer_collection_id: str,
) -> tuple[dict[str, Any], Any]:
    method = "GET"
    headers = {
        "If-None-Match": dialogue_etag,
    }
    payload: dict[str, Any] = {}
    endpoint = "/trip-offers/trip-offer-collections/{0}".format(
        trip_offer_collection_id,
    )
    await asyncio.sleep(10)
    return await make_br_request(
        config_manager,
        method,
        endpoint,
        payload,
        headers,
    )


async def br_trip_collections(
    config_manager: ConfigurationManager,
    dialogues_id: str,
    dialogue_etag: str,
    ids_list: Sequence[Mapping[str, str]],
    passenger_ids: str,
    departure_after: str,
) -> int:
    trip_offers_list = []
    for ids in ids_list:
        trip_filter_data = await br_trip_filter(
            config_manager,
            dialogues_id,
            dialogue_etag,
            departure_after,
            ids,
        )
        trip_filter_id = trip_filter_data[0]["result"]["id"]
        dialogue_etag1 = trip_filter_data[1]["ETag"]

        trip_offer_filter_data = await br_trip_offer_filter(
            config_manager,
            dialogues_id,
            passenger_ids,
            dialogue_etag1,
            trip_filter_id,
        )
        trip_offer_collection_id = trip_offer_filter_data[0]["result"]["id"]
        dialogue_etag2 = trip_offer_filter_data[1]["ETag"]

        trip_offer_collection_data = await br_trip_offer_collection(
            config_manager,
            dialogue_etag2,
            trip_offer_collection_id,
        )
        assert trip_offer_collection_data[0], "trip-offer-collections Results is empty"
        trip_offers_list = trip_offer_collection_data[0]["result"]["tripOffers"]
    return len(trip_offers_list)


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
