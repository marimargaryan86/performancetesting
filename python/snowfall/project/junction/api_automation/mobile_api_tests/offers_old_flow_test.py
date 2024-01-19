import datetime
import logging
from collections.abc import Sequence
from typing import Any

import allure
import pytest

from snowfall.project.junction.api_automation.test_functions.helper import (
    wait_for_response,
    wait_until_completed,
)
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


async def get_place_id(
    mobile_client: MobileApiClient,
    country_codes: Sequence[str],
) -> list[str]:
    place_ids = []
    for code in country_codes:
        response = await mobile_client.get_places(code)
        place_ids.append(response["data"][0]["id"])
    return place_ids


async def create_trip_search(
    mobile_client: MobileApiClient,
    departure_after: datetime.datetime,
    origin: str,
    destination: str,
) -> str:
    response = await mobile_client.create_trip_search(
        origin,
        destination,
        departure_after,
    )
    return response["data"]["id"]


async def get_trips_list(
    mobile_client: MobileApiClient,
    create_trip_search_id: str,
) -> Any:
    return await mobile_client.get_trips_list(create_trip_search_id)


async def create_offer_search(
    mobile_client: MobileApiClient,
    trips_list: Sequence[str],
) -> Sequence[str]:
    year = 1980
    month = 2
    day = 3

    passenger_date_of_birth = [datetime.date(year, month, day)]
    offer_search_ids = []
    for trip_id in trips_list:
        response = await mobile_client.create_offers_search(
            trip_id,
            passenger_date_of_birth,
        )
        offer_search_ids.append(response["data"]["id"])
    return offer_search_ids


async def get_offer_search(
    mobile_client: MobileApiClient,
    offer_searches_id: str,
) -> Any:
    offers_searches = await mobile_client.get_offer_search(offer_searches_id)
    return offers_searches["data"]


async def get_option_id(  # noqa: WPS231
    offer_id: str,
    offer_list: dict[str, Any],
) -> str:
    option_id = ""
    offer_group_id = ""
    offer_data = offer_list["data"][0]
    offer_list_included = offer_list["included"]

    if offer_data["id"] == offer_id:
        offer_groups = offer_data["relationships"]["groups"]
        offer_group_id = offer_groups["data"][0]["id"]

    for offer_item in offer_list_included:
        if offer_item.get("id") == offer_group_id:
            options = offer_item.get("relationships", {}).get("options", [])
            option_id = options["data"][0]["id"]

    return option_id


async def list_offers_by_offer_search(
    mobile_client: MobileApiClient,
    offers_list: Sequence[str],
) -> list[dict[str, Any]]:
    offer_list = []
    for offer_search_id in offers_list:
        response = await mobile_client.list_offers_by_offer_search(
            offer_search_id,
        )
        if response["data"]:
            if "included" in response:
                offer_id = response["data"][0]["id"]
                await get_option_id(offer_id, response)
            offer = response["data"][0]
            groups = offer["relationships"]["groups"]["data"]
            for group in groups:
                included_data = response["included"]
                group_index = next(
                    (
                        index
                        for index, opt_data in enumerate(included_data)
                        if "id" in opt_data and opt_data["id"] == group["id"]
                    ),
                    None,
                )
                options = response["included"][group_index]["relationships"]["options"]
                option_id = options["data"][0]["id"]
                offer_list.append(
                    {
                        "offer_id": offer["id"],
                        "groups_id": group["id"],
                        "option_ids": [option_id],
                    },
                )
                return offer_list
    return []


async def get_completed_offer_search(
    mobile_client: MobileApiClient,
    offer_searches_id: str,
) -> Any:
    return await wait_until_completed(
        lambda: get_offer_search(mobile_client, offer_searches_id),
        "Timeout reached and status was not completed.",
    )


iata_codes = [
    [("stockholm", "london"), ("london", "athens")],
    ("london", "vienna"),
    ("chicago", "groningen"),
]
ids = [
    "Ask2Go",
    "Duffel",
    "Multi-modal",
]


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.integration()
@pytest.mark.parametrize("iata_codes", iata_codes, ids=ids)
async def test_offers_old_flow(  # noqa: WPS217
    mobile_client: MobileApiClient,
    departure_after: datetime.datetime,
    iata_codes: str,
) -> None:
    with allure.step("Step to log getting the origin and destination"):
        origin, destination = await get_place_id(mobile_client, iata_codes)
        allure.attach(
            "origin : {0}, destination : {1}".format(origin, destination),
            "text/plain",
        )

    with allure.step("Step to log create trip search"):
        create_trip_search_id = await create_trip_search(
            mobile_client,
            departure_after,
            origin,
            destination,
        )
        allure.attach(
            "Trip search ID: {0}".format(create_trip_search_id),
            "text/plain",
        )

    with allure.step("Step to log get trip search"):
        trips_search = await wait_for_response(
            lambda: get_trips_list(mobile_client, create_trip_search_id),
            "Timeout reached with no trips found.",
        )
        allure.attach(
            "Trip search ID: {0}".format(create_trip_search_id),
            "text/plain",
        )

    with allure.step("Step to log create offer search"):
        trips_list = [trip["id"] for trip in trips_search["data"]]
        assert trips_list, "no trips found"

        offer_searches = await create_offer_search(mobile_client, trips_list)
        allure.attach(
            "Offer searches: {0}".format(offer_searches),
            "text/plain",
        )

    with allure.step("Step to log get offer search"):
        for offer_id_search in offer_searches:
            await get_completed_offer_search(mobile_client, offer_id_search)
        allure.attach(
            "Offer searches: {0}".format(offer_searches),
            "text/plain",
        )

    with allure.step("Step to log get offers list by offer search"):
        offer_list = await list_offers_by_offer_search(mobile_client, offer_searches)
        assert offer_list, "no offers"
        keys_to_check = ["offer_id", "groups_id", "option_ids"]
        assert all(
            offer.get(key) != "" for offer in offer_list for key in keys_to_check
        ), "no offers found"
        offer_id = offer_list[0]["offer_id"]
        option_id = offer_list[0]["option_ids"]
        assert offer_id
        assert option_id
        allure.attach(
            "Offers list by searches: {0}".format(offer_list),
            "text/plain",
        )


@pytest.mark.smoke()
@pytest.mark.parametrize("iata_codes", iata_codes, ids=ids)
async def test_booking_flow_smoke(  # noqa: WPS217
    mobile_client: MobileApiClient,
    departure_after: datetime.datetime,
    iata_codes: str,
) -> None:
    with allure.step("Step to log getting the origin and destination"):
        origin, destination = await get_place_id(mobile_client, iata_codes)
        allure.attach(
            "origin : {0}, destination : {1}".format(origin, destination),
            "text/plain",
        )

    with allure.step("Step to log create trip search"):
        create_trip_search_id = await create_trip_search(
            mobile_client,
            departure_after,
            origin,
            destination,
        )
        allure.attach(
            "Trip search ID: {0}".format(create_trip_search_id),
            "text/plain",
        )

    with allure.step("Step to log get trip search"):
        trips_search = await wait_for_response(
            lambda: get_trips_list(mobile_client, create_trip_search_id),
            "Timeout reached with no trips found.",
        )
        allure.attach(
            "Trip search ID: {0}".format(create_trip_search_id),
            "text/plain",
        )

    with allure.step("Step to log create offer search"):
        trips_list = [trip["id"] for trip in trips_search["data"]]
        assert trips_list, "no trips found"

        offer_searches = await create_offer_search(mobile_client, trips_list)
        allure.attach(
            "Offer searches: {0}".format(offer_searches),
            "text/plain",
        )

    with allure.step("Step to log get offer search"):
        for offer_id_search in offer_searches:
            await get_completed_offer_search(mobile_client, offer_id_search)
        allure.attach(
            "Offer searches: {0}".format(offer_searches),
            "text/plain",
        )

    with allure.step("Step to log get offers list by offer search"):
        offer_list = await list_offers_by_offer_search(mobile_client, offer_searches)
        assert offer_list, "no offers"
        keys_to_check = ["offer_id", "groups_id", "option_ids"]
        assert all(
            offer.get(key) != "" for offer in offer_list for key in keys_to_check
        ), "no offers found"
        offer_id = offer_list[0]["offer_id"]
        option_id = offer_list[0]["option_ids"]
        assert offer_id
        assert option_id
        allure.attach(
            "Offers list by searches: {0}".format(offer_list),
            "text/plain",
        )
