import asyncio
import datetime
import json
import logging
import time
from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.vendor.junction.go.models import (
    Address,
    ContactDetails,
    Passenger,
    TravelerDocument,
)

PASSENGERS = (
    Passenger(
        first_name="John",
        last_name="Smith",
        title="mr",
        gender="male",
        date_of_birth="1980-02-03",
        traveler_document=TravelerDocument(
            document_type="passport",
            document_number="1543343434",
            document_issue_country="GB",
            document_expiration_date="2025-02-03",
            nationality="ES",
            residence_country_code="NL",
        ),
    ),
    Passenger(
        first_name="John",
        last_name="Smith",
        title="mr",
        gender="male",
        date_of_birth="1999-02-03",
        traveler_document=TravelerDocument(
            document_type="passport",
            document_number="9876543211",
            document_issue_country="GB",
            document_expiration_date="2029-02-03",
            nationality="ES",
            residence_country_code="NL",
        ),
    ),
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
) -> Sequence[str]:
    response = await mobile_client.get_trips_list(create_trip_search_id)
    return [trip["id"] for trip in response["data"]]


async def create_offer_lists(  # noqa: WPS210
    mobile_client: MobileApiClient,
    trips_list: Sequence[str],
) -> list[dict[str, Any]]:
    year = 1980
    month = 2
    day = 3

    passenger_date_of_birth = [datetime.date(year, month, day)]
    offer_list = []
    for trip_id in trips_list:
        response = await mobile_client.create_offers_search(
            trip_id,
            passenger_date_of_birth,
        )
        trip_offer_searches = response["data"]["id"]
        await asyncio.sleep(5)
        response = await mobile_client.list_offers_by_offer_search(
            trip_offer_searches,
        )
        option_ids = []
        if response["data"]:
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
                option_ids.append(option_id)
                offer_list.append(
                    {
                        "offer_id": offer["id"],
                        "groups_id": group["id"],
                        "options_id": option_ids,
                    },
                )
    return offer_list


async def create_quote(  # noqa: WPS210
    mobile_client: MobileApiClient,
    offer_id: str,
    option_ids: Sequence[str],
) -> str:
    quote = await mobile_client.create_offer_price_quote(
        offer_id=offer_id,
        option_ids=option_ids,
    )
    return quote["data"]["id"]


async def get_quote(
    mobile_client: MobileApiClient,
    quote: str,
) -> Mapping[str, Any]:
    get_quotes = await mobile_client.get_offer_price_quote(
        offer_price_quote_id=quote,
    )
    return get_quotes["data"]


async def create_payment(
    mobile_client: MobileApiClient,
    quote: Mapping[str, Any],
) -> str:
    currency = quote["data"]["attributes"]["price"]["currency"]
    amount = quote["data"]["attributes"]["price"]["amount"]
    resp = await mobile_client.create_payment(currency=currency, amount=amount)
    logger.info("Get payment data %s", json.dumps(resp, indent=4))
    return resp["data"]


async def create_order(  # noqa: WPS210
    mobile_client: MobileApiClient,
    quote_id: str,
    payment: str,
) -> Mapping[str, Any]:
    contact_details = ContactDetails(
        email="john.smith@example.com",
        phone_number="+37495878787",
        address=Address(
            address_lines=[
                "Street name 7",
            ],
            country_code="GB",
            postal_code="12345",
            city="London",
        ),
    )
    residence_address = Address(
        address_lines=[
            "Street name 7",
        ],
        country_code="GB",
        postal_code="12345",
        city="London",
    )

    order = await mobile_client.create_order_with_payment(
        quote_id=quote_id,
        passengers=PASSENGERS,
        contact_details=contact_details,
        payment_id=payment,
        address=residence_address,
    )
    return order["data"]


async def wait_for_response(
    request_func: Any,
    error_message: str,
    max_wait_time_seconds: int = 60,
    polling_interval: int = 5,
) -> Any:
    stopwatch = time.time()

    while True:
        response = await request_func()

        if response:
            return response

        elapsed_time = time.time() - stopwatch
        if elapsed_time <= max_wait_time_seconds:
            await asyncio.sleep(polling_interval)
        else:
            raise AssertionError(error_message)


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


@pytest.mark.integration()
@pytest.mark.parametrize("iata_codes", iata_codes, ids=ids)
async def test_booking_flow(  # noqa: WPS217, WPS210
    mobile_client: MobileApiClient,
    departure_after: datetime.datetime,
    iata_codes: str,
) -> None:
    origin, destination = await get_place_id(mobile_client, iata_codes)

    create_trip_search_id = await create_trip_search(
        mobile_client,
        departure_after,
        origin,
        destination,
    )
    trips_list = await wait_for_response(
        lambda: get_trips_list(mobile_client, create_trip_search_id),
        "Timeout reached with no trips found.",
    )
    assert trips_list, "no trips found"
    offer_list = await wait_for_response(
        lambda: create_offer_lists(mobile_client, trips_list),
        "Timeout reached with no offers found.",
    )
    assert offer_list, "no offers"
    keys_to_check = ["offer_id", "groups_id", "options_id"]
    assert all(
        offer.get(key) != "" for offer in offer_list for key in keys_to_check
    ), "no offers found"
    offer_id = offer_list[0]["offer_id"]
    option_id = offer_list[0]["options_id"]
    quotes = await wait_for_response(
        lambda: create_quote(mobile_client, offer_id, option_id),
        "Timeout reached with no quotes found.",
    )
    assert quotes, "no quotes for offer"
    get_quote_id = await wait_for_response(
        lambda: get_quote(mobile_client, quotes),
        "Timeout reached with no quotes Id found.",
    )
    assert get_quote_id


@pytest.mark.smoke()
@pytest.mark.parametrize("iata_codes", iata_codes, ids=ids)
async def test_booking_flow_smoke(  # noqa: WPS217, WPS210
    mobile_client: MobileApiClient,
    departure_after: datetime.datetime,
    iata_codes: str,
) -> None:
    origin, destination = await get_place_id(mobile_client, iata_codes)
    create_trip_search_id = await create_trip_search(
        mobile_client,
        departure_after,
        origin,
        destination,
    )
    trips_list = await wait_for_response(
        lambda: get_trips_list(mobile_client, create_trip_search_id),
        "Timeout reached with no trips found.",
    )
    assert trips_list, "no trips found"
    offer_list = await wait_for_response(
        lambda: create_offer_lists(mobile_client, trips_list),
        "Timeout reached with no offers found.",
    )
    keys_to_check = ["offer_id", "groups_id", "options_id"]
    assert all(
        offer.get(key) != "" for offer in offer_list for key in keys_to_check
    ), "no offers found"
