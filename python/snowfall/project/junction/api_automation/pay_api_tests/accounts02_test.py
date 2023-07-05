import json
import logging
from collections.abc import Mapping
from typing import Any

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import EXIT_MSG
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    return_randomized_token,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_create_account(
    pay_admin_client: PayAdminClient,
    pay_create_contact: Mapping[str, Any],
) -> None:
    name = "test account {0}".format(return_randomized_token())
    try:
        response_create_account = await pay_admin_client.create_accounts(
            name,
            pay_create_contact["data"]["id"],
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_account: %s", err.response.headers)
        logger.info("response_create_account body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)
    logger.info(
        "response_create_account: %s",
        json.dumps(response_create_account, indent=4),
    )

    assert "https" in response_create_account["data"]["links"]["self"]
