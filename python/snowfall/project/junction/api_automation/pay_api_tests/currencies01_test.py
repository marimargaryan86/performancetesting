import json
import logging
import sys

import httpx
import pytest

from snowfall.vendor.pay.client import PayAdminClient, PayClient

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration
async def test_get_currencies(
    pay_client: PayClient,
    pay_admin_client: PayAdminClient,
) -> None:
    try:
        response_list_all_currencies = await pay_client.list_all_currencies(
            limit=100,
            sort="id",
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_list_all_currencies err: %s", err.response.headers)
        logger.info("response_list_all_currencies body: %s", err.response.json())
        sys.exit(EXIT_MSG)
    logger.info(
        "list_all_currencies: %s",
        json.dumps(response_list_all_currencies, indent=4),
    )
    expected_currencies_list = [
        "AUD",
        "BHD",
        "BGN",
        "CAD",
        "CNY",
        "CZK",
        "DKK",
        "EUR",
        "HKD",
        "HUF",
        "ILS",
        "JPY",
        "KES",
        "KWD",
        "NZD",
        "NOK",
        "OMR",
        "PLN",
        "QAR",
        "RON",
        "SAR",
        "SGD",
        "ZAR",
        "SEK",
        "CHF",
        "THB",
        "TRY",
        "UGX",
        "GBP",
        "AED",
        "USD",
    ]
    actual_currencies_list = []
    for currency_entry_value in response_list_all_currencies["data"]:
        actual_currencies_list.append(currency_entry_value["id"])

    logger.info("expected_currencies_list: %s", expected_currencies_list)
    logger.info("actual_currencies_list: %s", actual_currencies_list)

    assert set(expected_currencies_list) == set(
        actual_currencies_list,
    ), "Expected currencies list lenght does not match"
