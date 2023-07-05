import json
import logging
from collections.abc import Mapping
from typing import Any

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_get_account(
    pay_admin_client: PayAdminClient,
    pay_list_accounts: Mapping[str, Any],
) -> None:
    try:
        response_get_account = await pay_admin_client.get_account(
            pay_list_accounts["data"][0]["id"],
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_get_account: %s", err.response.headers)
        logger.info("response_get_account body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)
    logger.info(
        "response_create_account: %s",
        json.dumps(response_get_account, indent=4),
    )

    assert "https" in response_get_account["data"]["links"]["self"]
