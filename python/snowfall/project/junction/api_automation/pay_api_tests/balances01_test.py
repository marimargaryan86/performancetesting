import json
import logging

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import PAY_TEST_ACCOUNT01
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_get_balances(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
) -> None:
    account_id = PAY_TEST_ACCOUNT01

    try:
        response_get_balances = await pay_admin_client.get_balances(account_id)
    except httpx.HTTPStatusError as err:
        logger.info("response_get_balances err: %s", err.response.headers)
        logger.info("response_get_balances body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)
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
    assert first_entry["relationships"]["account"]["data"]["type"] == "accounts"
    assert is_valid_uuid(first_entry["relationships"]["account"]["data"]["id"])
    assert isinstance(first_entry["relationships"]["currency"]["data"]["id"], str)
    assert first_entry["relationships"]["currency"]["data"]["type"] == "currencies"
