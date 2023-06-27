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
async def test_update_account(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
    pay_create_account: Mapping[str, Any],
) -> None:
    try:
        response_update_account = await pay_admin_client.update_account(
            pay_create_account["data"]["id"],
            "disabled",
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_update_account: %s", err.response.headers)
        logger.info("response_update_account body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
    logger.info(
        "response_update_account: %s",
        json.dumps(response_update_account, indent=4),
    )
    assert pay_create_account["data"]["attributes"]["status"] == "enabled"
    assert response_update_account["data"]["attributes"]["status"] == "disabled"
    assert "https" in response_update_account["data"]["links"]["self"]
