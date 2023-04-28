import json
import logging
from typing import Any, Mapping

import httpx
import pytest
from dateutil import parser

from snowfall.project.junction.api_automation.conftest import EXIT_MSG
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.vendor.junction.pay.client import Client

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_get_transactions(  # noqa: WPS218
    pay_client: Client,
    pay_admin_client: PayAdminClient,
    get_mongo_config: Mapping[str, Any],
    pay_create_transaction: Mapping[str, Any],
) -> None:
    try:
        response_get_transactions = await pay_admin_client.get_transactions()
    except httpx.HTTPStatusError as err4:
        logger.info("response_get_transactions err:: %s", err4.response.headers)
        logger.info("response_get_transactions body: %s", err4.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info(
        "get_transactions: %s",
        json.dumps(
            response_get_transactions,
            indent=4,
        ),
    )

    first_item = response_get_transactions["data"][0]
    assert is_valid_uuid(first_item["id"])
    assert first_item["type"] == "transactions"
    assert is_valid_uuid(first_item["attributes"]["externalReference"])
    assert first_item["attributes"]["createdAt"]
    try:
        is_valid_date = bool(
            parser.parse(
                first_item["attributes"]["createdAt"],
            ),
        )
    except parser.ParserError:
        is_valid_date = False
    assert is_valid_date
    assert isinstance(
        first_item["attributes"]["amounts"]["beneficiary"]["currency"],
        str,
    )
    assert isinstance(first_item["attributes"]["amounts"]["beneficiary"]["amount"], int)
    assert isinstance(first_item["attributes"]["amounts"]["quotation"]["currency"], str)
    assert isinstance(first_item["attributes"]["amounts"]["quotation"]["amount"], int)
    assert isinstance(
        first_item["attributes"]["amounts"]["baseConverted"]["currency"],
        str,
    )
    assert isinstance(
        first_item["attributes"]["amounts"]["baseConverted"]["amount"],
        int,
    )
    assert isinstance(
        first_item["attributes"]["amounts"]["salesMargin"]["currency"],
        str,
    )
    assert isinstance(first_item["attributes"]["amounts"]["salesMargin"]["amount"], int)
    assert isinstance(first_item["attributes"]["amounts"]["fxMargin"]["currency"], str)
    assert isinstance(first_item["attributes"]["amounts"]["fxMargin"]["amount"], int)
    assert isinstance(
        first_item["attributes"]["amounts"]["fxProviderMargin"]["currency"],
        str,
    )
    assert isinstance(
        first_item["attributes"]["amounts"]["fxProviderMargin"]["amount"],
        int,
    )
    assert isinstance(first_item["attributes"]["rates"]["fxQuote"], float)
    assert isinstance(first_item["attributes"]["rates"]["fxBuffer"], float)
    assert isinstance(first_item["attributes"]["rates"]["salesMarkup"], float)
    assert isinstance(first_item["attributes"]["rates"]["fxMarkup"], float)
    assert is_valid_uuid(first_item["relationships"]["conversion"]["data"]["id"])
    assert first_item["relationships"]["conversion"]["data"]["type"] == "conversions"
    assert is_valid_uuid(first_item["relationships"]["payer"]["data"]["id"])
    assert first_item["relationships"]["payer"]["data"]["type"] == "companies"
    assert is_valid_uuid(first_item["relationships"]["beneficiary"]["data"]["id"])
    assert first_item["relationships"]["beneficiary"]["data"]["type"] == "companies"
