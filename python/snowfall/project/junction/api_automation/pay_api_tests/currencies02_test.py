import json
import logging
from collections.abc import Mapping
from typing import Any

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import EXIT_MSG
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_add_currency(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
    pay_create_account: Mapping[str, Any],
) -> None:
    currency_id = "USD"
    try:
        response_add_currency = await pay_admin_client.add_currency(
            account_id=pay_create_account["data"]["id"],
            currency_id=currency_id,
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_add_currency err: %s", err.response.headers)
        logger.info("response_add_currency body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)
    logger.info(
        "response_add_currency: %s",
        json.dumps(response_add_currency, indent=4),
    )

    assert is_valid_uuid(response_add_currency["data"]["id"])
    assert response_add_currency["data"]["type"] == "balances"
    assert response_add_currency["data"]["attributes"]["amount"] == 0
    relationships = response_add_currency["data"]["relationships"]
    assert is_valid_uuid(relationships["account"]["data"]["id"])
    assert relationships["account"]["data"]["type"] == "accounts"
    assert relationships["currency"]["data"]["id"] == currency_id
    assert relationships["currency"]["data"]["type"] == "currencies"
