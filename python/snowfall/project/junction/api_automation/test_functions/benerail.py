import asyncio
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from snowfall.project.junction.api_automation.conftest import (
    ConfigurationManager,
    make_br_request,
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
        trip_offers_list = trip_offer_collection_data[0]["result"]["tripOffers"]
    return len(trip_offers_list)
