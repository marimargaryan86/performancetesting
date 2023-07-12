import asyncio
import datetime
import logging
from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


async def get_place_id(
    mobile_client: MobileApiClient,
) -> list[str]:
    place_ids = []
    country_codes = ["lon", "gre"]
    for code in country_codes:
        response = await mobile_client.get_places(code)
        place_ids.append(response["data"][0]["id"])
    return place_ids


async def create_trip_search(
    mobile_client: MobileApiClient,
    departure_after: datetime.datetime,
) -> str:
    ids = await get_place_id(mobile_client)
    origin = ids[0]
    destination = ids[1]
    response = await mobile_client.create_trip_search(
        origin,
        destination,
        departure_after,
    )
    return response["data"]["id"]


async def get_trips_list(
    mobile_client: MobileApiClient,
    departure_after: datetime.datetime,
) -> Sequence[str]:
    create_trip_search_d = await create_trip_search(mobile_client, departure_after)
    await asyncio.sleep(5)
    response = await mobile_client.get_trips_list(create_trip_search_d)
    return [trip["id"] for trip in response["data"]]


async def trip_id_has_offers(  # noqa: WPS210
    mobile_client: MobileApiClient,
    departure_after: datetime.datetime,
) -> Sequence[Mapping[str, Any]]:
    trips_list = await get_trips_list(mobile_client, departure_after)
    offer_list = []
    year = 1980
    month = 2
    day = 3
    passenger_date_of_birth = [datetime.date(year, month, day)]
    session_token = "YMSXrOAhIOdvIbxAmfSt7vJtRBkurNb6"
    for trip_id in trips_list:
        response = await mobile_client.create_offers_search(
            trip_id,
            passenger_date_of_birth,
            session_token,
        )
        trip_offer_searches = response["data"]["id"]
        await asyncio.sleep(5)
        response = await mobile_client.get_offer_search(trip_offer_searches)
        if response["data"]["attributes"]["status"] == "completed":
            response = await mobile_client.list_offers_by_offer_search(
                trip_offer_searches,
            )
            if response["data"]:
                offer = response["data"][0]
                group = offer["relationships"]["groups"]["data"][0]
                offer_list.append({"offer_id": offer["id"], "groups_id": group["id"]})
                break

    return offer_list


@pytest.mark.integration()
async def test_booking_flow(
    mobile_client: MobileApiClient,
    departure_after: datetime.datetime,
) -> None:
    trips_id_offer = await trip_id_has_offers(mobile_client, departure_after)
    assert trips_id_offer, "The result of trip_id_has_offers is empty"
    offer_id = trips_id_offer[0]["offer_id"]
    assert is_valid_uuid(offer_id) is True, "no offers"
