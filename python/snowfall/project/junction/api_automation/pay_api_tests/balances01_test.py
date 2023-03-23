import json
import logging
import sys
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.pay.client import PayAdminClient

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration
async def test_get_balances(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
    pay_get_accounts: Mapping[str, Any],
) -> None:
    account_id = pay_get_accounts["data"][0]["id"]

    try:
        response_get_balances = await pay_admin_client.get_balances(account_id)
    except httpx.HTTPStatusError as err:
        logger.info("response_get_balances err: %s", err.response.headers)
        logger.info("response_get_balances body: %s", err.response.json())
        sys.exit(EXIT_MSG)

    logger.info(
        "response_get_balances: %s",
        json.dumps(
            response_get_balances,
            indent=4,
        ),
    )

    first_entry = response_get_balances["data"][0]
    assert is_valid_uuid(first_entry["id"])
    assert first_entry["type"] == "balances"
    assert isinstance(first_entry["attributes"]["amount"], int)
    assert is_valid_uuid(first_entry["relationships"]["account"]["data"]["id"])
    assert first_entry["relationships"]["company"]["data"]["type"] == "accounts"
    assert is_valid_uuid(first_entry["relationships"]["contact"]["data"]["id"])
    assert isinstance(first_entry["relationships"]["currency"]["data"]["id"], str)
    assert first_entry["relationships"]["currency"]["data"]["type"] == "currencies"
