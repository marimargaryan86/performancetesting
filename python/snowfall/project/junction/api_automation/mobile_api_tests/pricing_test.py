import asyncio
import time
from collections.abc import Mapping, Sequence
from typing import Any

import allure
import pytest

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)


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


async def wait_until_completed(
    request_func: Any,
    error_message: str,
    max_wait_time_seconds: int = 120,
    polling_interval: int = 5,
) -> Any:
    stopwatch = time.time() + max_wait_time_seconds

    while stopwatch - time.time() > 0:
        response = await request_func()
        if response["attributes"]["status"] == "completed":
            return response
        await asyncio.sleep(polling_interval)

    raise AssertionError(error_message)


@pytest.mark.manually()
async def test_pricing_flow(
    mobile_client: MobileApiClient,
) -> None:
    offer_id = "cd0d9e47-db99-4a1f-b7bc-47747ff41f81"
    option_id = "5872f9dc-e315-5567-9f26-2dcfd4c8744b"

    quotes = await create_quote(mobile_client, offer_id, [option_id])
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
    with allure.step("Step to Create quotes"):
        allure.attach(
            "Quote with currency: {0} and amount {1}".format(
                currency,
                amount,
            ),
            "text/plain",
        )

    payment = await create_payment(
        mobile_client,
        currency,
        amount,
    )
    assert payment
    with allure.step("Step to Create quotes"):
        allure.attach(
            "Payment ID: {0}".format(payment),
            "text/plain",
        )
