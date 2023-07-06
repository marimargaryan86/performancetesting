import json
import logging

import pytest
from httpx import HTTPStatusError

from snowfall.project.junction.api_automation.test_functions.helpers_api import with_log
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.skip(reason="temporary skipped")
async def test_create_payment(mobile_client: MobileApiClient) -> None:
    try:  # noqa: WPS229
        resp = await mobile_client.create_payment(currency="EUR", amount="3.14")
        logger.info("create_payment: %s", json.dumps(resp, indent=4))
        assert "id" in resp["data"]
    except HTTPStatusError as err:
        logger.info("test_create_payment err: %s", err.response.headers)
        logger.info("test_create_payment body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)


@pytest.mark.skip(reason="temporary skipped")
async def test_update_payment(mobile_client: MobileApiClient) -> None:
    resp = await with_log(mobile_client.create_payment)(currency="USD", amount="3.50")
    payment_id = resp["data"]["id"]
    status = await with_log(mobile_client.update_payment)(
        payment_intent_id=payment_id,
        voucher_id="ABC00032",
    )
    assert status == 204
