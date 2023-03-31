import json
import logging
import sys
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration()
async def test_get_balances(  # noqa: WPS210, WPS218
    pay_admin_client: PayAdminClient,
    pay_create_account: Mapping[str, Any],
) -> None:
    account_id = pay_create_account["data"]["id"]

    response_get_balances = await return_get_balances(account_id, pay_admin_client)

    assert bool(response_get_balances["data"]) is False

    currency_id = "USD"
    try:
        response_add_currency = await pay_admin_client.add_currency(
            account_id=account_id,
            currency_id=currency_id,
        )
    except httpx.HTTPStatusError as err2:
        logger.info("response_add_currency err: %s", err2.response.headers)
        logger.info("response_add_currency body: %s", err2.response.json())
        sys.exit(EXIT_MSG)
    logger.info(
        "response_add_currency: %s",
        json.dumps(response_add_currency, indent=4),
    )

    response_get_balances2 = await return_get_balances(account_id, pay_admin_client)

    first_entry = response_get_balances2["data"][0]
    assert is_valid_uuid(first_entry["id"])
    assert first_entry["type"] == "balances"
    assert isinstance(first_entry["attributes"]["amount"], int)
    assert is_valid_uuid(first_entry["relationships"]["account"]["data"]["id"])
    assert first_entry["relationships"]["account"]["data"]["type"] == "accounts"
    assert is_valid_uuid(first_entry["relationships"]["account"]["data"]["id"])
    assert isinstance(first_entry["relationships"]["currency"]["data"]["id"], str)
    assert first_entry["relationships"]["currency"]["data"]["type"] == "currencies"


async def return_get_balances(
    account_id: str,
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
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
    return response_get_balances
