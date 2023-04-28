import json
import logging
from typing import Any, Mapping

import httpx
import pytest
from dateutil import parser

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
async def test_get_conversion_details(  # noqa: WPS218
    pay_client: Client,
    pay_admin_client: PayAdminClient,
    pay_create_transaction: Mapping[str, Any],
) -> None:
    conversion = pay_create_transaction["data"]["relationships"]["conversion"]["data"]
    try:
        rgcd = await pay_admin_client.get_conversion_details(
            conversion["id"],
            include=["transactions"],
        )
    except httpx.HTTPStatusError as err:
        logger.info("response err: %s", err.response.headers)
        logger.info("response_create_transactions body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)

    logger.info("get_conversion_details: %s", json.dumps(rgcd, indent=4))

    rgcd_data = rgcd["data"]

    assert is_valid_uuid(rgcd_data["id"])
    assert rgcd_data["type"] == "conversions"
    parser.parse(rgcd_data["attributes"]["createdAt"])
    parser.parse(rgcd_data["attributes"]["settledAt"])
    assert isinstance(rgcd_data["attributes"]["sellAmount"]["currency"], str)
    assert isinstance(rgcd_data["attributes"]["sellAmount"]["amount"], int)
    assert isinstance(rgcd_data["attributes"]["buyAmount"]["currency"], str)
    assert isinstance(rgcd_data["attributes"]["buyAmount"]["amount"], int)
    assert isinstance(rgcd_data["attributes"]["executedRate"], float)
    assert isinstance(rgcd_data["attributes"]["fxDelta"], float)
    assert isinstance(rgcd_data["attributes"]["fxStatus"], str)
    assert is_valid_uuid(rgcd_data["relationships"]["transactions"]["data"]["id"])
    assert rgcd_data["relationships"]["transactions"]["data"]["type"] == "transactions"
    assert "https" in rgcd_data["links"]["self"]
    assert rgcd["included"][0]["id"] == pay_create_transaction["data"]["id"]

    all_included = rgcd["included"]
    transactions_list = [one_include["id"] for one_include in all_included]
    assert pay_create_transaction["data"]["id"] in transactions_list
