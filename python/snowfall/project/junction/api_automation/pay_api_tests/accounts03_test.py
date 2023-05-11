import json
import logging
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


@pytest.mark.integration()
async def test_get_account(  # noqa: WPS218
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

    assert is_valid_uuid(response_get_account["data"]["id"])
    assert response_get_account["data"]["type"] == "accounts"
    assert isinstance(response_get_account["data"]["attributes"]["name"], str)
    assert isinstance(response_get_account["data"]["attributes"]["status"], str)
    relationships = response_get_account["data"]["relationships"]
    assert is_valid_uuid(relationships["company"]["data"]["id"])
    assert relationships["company"]["data"]["type"] == "companies"
    assert is_valid_uuid(relationships["contact"]["data"]["id"])
    assert relationships["contact"]["data"]["type"] == "contacts"
    assert "https" in response_get_account["data"]["links"]["self"]
