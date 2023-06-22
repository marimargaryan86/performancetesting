import json
import logging

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_get_accounts(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
) -> None:
    try:
        response_get_accounts = await pay_admin_client.get_accounts()
    except httpx.HTTPStatusError as err:
        logger.info("response_get_accounts err: %s", err.response.headers)
        logger.info("response_get_accounts body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info("get_accounts: %s", json.dumps(response_get_accounts, indent=4))
    first_entry = response_get_accounts["data"][0]
    assert "https" in first_entry["links"]["self"]
    assert "https" in response_get_accounts["links"]["next"]
