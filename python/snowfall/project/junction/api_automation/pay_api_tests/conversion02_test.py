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
async def test_list_conversions_details(  # noqa: WPS218
    pay_client: Client,
    pay_admin_client: PayAdminClient,
    pay_create_transaction: Mapping[str, Any],
) -> None:
    try:
        response_list_conversions_details = (
            await pay_admin_client.list_conversions_details(include=["transactions"])
        )
    except httpx.HTTPStatusError as err:
        logger.info("response err: %s", err.response.headers)
        logger.info("response_create_transactions body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info(
        "list_conversions_details: %s",
        json.dumps(response_list_conversions_details, indent=4),
    )

    rlcd_first_item = response_list_conversions_details["data"][0]

    assert is_valid_uuid(rlcd_first_item["id"])
    assert rlcd_first_item["type"] == "conversions"
    parser.parse(rlcd_first_item["attributes"]["createdAt"])
    parser.parse(rlcd_first_item["attributes"]["settledAt"])
    assert isinstance(rlcd_first_item["attributes"]["sellAmount"]["currency"], str)
    assert isinstance(rlcd_first_item["attributes"]["sellAmount"]["amount"], int)
    assert isinstance(rlcd_first_item["attributes"]["buyAmount"]["currency"], str)
    assert isinstance(rlcd_first_item["attributes"]["buyAmount"]["amount"], int)
    assert isinstance(rlcd_first_item["attributes"]["executedRate"], float)
    assert isinstance(rlcd_first_item["attributes"]["fxDelta"], type(None) | float)
    assert isinstance(rlcd_first_item["attributes"]["fxStatus"], str)
    assert is_valid_uuid(rlcd_first_item["relationships"]["transactions"]["data"]["id"])
    assert (
        rlcd_first_item["relationships"]["transactions"]["data"]["type"]
        == "transactions"
    )
    assert "https" in rlcd_first_item["links"]["self"]

    assert len(response_list_conversions_details["included"]) <= len(
        response_list_conversions_details["data"],
    )
    all_included = response_list_conversions_details["included"]
    transactions_list = [one_include["id"] for one_include in all_included]
    assert (
        rlcd_first_item["relationships"]["transactions"]["data"]["id"]
        in transactions_list
    )
