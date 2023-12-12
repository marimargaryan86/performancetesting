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
    stripe_confirmation,
    wait_until_completed,
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


async def get_search_offers(
    mobile_client: MobileApiClient,
    simple_offer_searches_id: str,
) -> Any:
    offers_searches = await mobile_client.get_offer_search(simple_offer_searches_id)
    return offers_searches["data"]


async def get_offer_list_simple_search(
    mobile_hub_client: MobileApiClient,
    offer_id_simple_search: str,
) -> dict[str, Any]:
    return await mobile_hub_client.list_offers_simple_search(
        offer_simple_search_id=offer_id_simple_search,
    )


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


async def create_quote(
    mobile_client: MobileApiClient,
    offer_id: str,
    option_ids: Sequence[str],
) -> str:
    quote = await mobile_client.create_offer_price_quote(
        offer_id=offer_id,
        option_ids=option_ids,
    )
    return quote["data"]["id"]


async def create_payment(
    mobile_client: MobileApiClient,
    currency: str,
    amount: str,
) -> str:
    quote = await mobile_client.create_payment(
        currency=currency,
        amount=amount,
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


places_pairs = [["Brussels-Midi", "Rotterdam Centraal"]]


@pytest.mark.manually()
@pytest.mark.parametrize("places_pairs", places_pairs)
async def test_simple_search(  # noqa: WPS217, WPS218
    mongo_client: MongoClient[Any],
    mobile_client: MobileApiClient,
    places_pairs: Sequence[tuple[Any, Any]],
    departure_after: datetime,
    stripe_api_key: str,
) -> None:
    origin_cord, destination_cord = await get_coordinates_by_place_name(
        mongo_client,
        places_pairs,
    )

    with allure.step("Step to log the origin and destination coordinates from DB"):
        allure.attach(
            "origin : {0}, destination : {1}".format(origin_cord, destination_cord),
            "text/plain",
        )

    assert origin_cord, "Origin not found"
    assert destination_cord, "Destination not found"
    await asyncio.sleep(10)
    offer_simple_search = await create_offer_simple_search(
        mobile_client,
        departure_after,
        origin_cord,
        destination_cord,
        [date(1980, 2, 3)],
        maximum_connections=2,
        allowed_segment_types=[LegType.rail],
    )
    offer_id_simple_search = offer_simple_search["data"]["id"]
    assert offer_id_simple_search, "offer is with simpl search wasn't found"

    with allure.step("Step to log create offer simple search"):
        allure.attach(
            "simple-offer-searches : {0}".format(offer_id_simple_search),
            "text/plain",
        )
    offer_search_data = await wait_until_completed(
        lambda: get_search_offers(mobile_client, offer_id_simple_search),
        "Timeout reached and status was not completed.",
    )

    assert offer_search_data
    with allure.step("Step to Get offers searches and validate status"):
        allure.attach(
            "Offer status is complited",
            "text/plain",
        )
    offers_list = await get_offer_list_simple_search(
        mobile_client,
        offer_id_simple_search,
    )

    offer_included = offers_list["included"]
    assert offer_included
    offer_id = offers_list["data"][0]["id"]
    offer_option_id = await get_option_id(offer_id, offers_list)
    assert offer_id
    assert offer_option_id
    with allure.step("Step to Get log offer id and offer option id"):
        allure.attach(
            "offer id: {0} and offer option id : {1}".format(offer_id, offer_option_id),
            "text/plain",
        )

    quotes = await create_quote(mobile_client, offer_id, [offer_option_id])
    assert quotes
    with allure.step("Step to Create quotes"):
        allure.attach(
            "Quotes ID {0}".format(quotes),
            "text/plain",
        )
    quote_data = await wait_until_completed(
        lambda: get_quote(mobile_client, quotes),
        "Timeout reached and status was not completed.",
    )
    assert quote_data
    currency = quote_data["attributes"]["price"]["currency"]
    amount = quote_data["attributes"]["price"]["amount"]
    with allure.step("Step to Get quotes"):
        allure.attach(
            "Quote with currency: {0} and amount {1}".format(
                currency,
                amount,
            ),
            "text/plain",
        )

    payment_intent_id = await create_payment(
        mobile_client,
        currency,
        amount,
    )
    assert payment_intent_id
    with allure.step("Step to Create Payment"):
        allure.attach(
            "Payment ID: {0}".format(payment_intent_id),
            "text/plain",
        )

    payment_intent = await stripe_confirmation(
        payment_intent_id=payment_intent_id,
        stripe_api_key=stripe_api_key,
    )
    assert payment_intent["status"] == "requires_capture"
    with allure.step("Step to Update Stripe Intent and Confirm"):
        allure.attach(
            "Payment Intent ID: {0}".format(payment_intent_id),
            "text/plain",
        )
