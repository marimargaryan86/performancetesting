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
async def test_get_payment(
    pay_admin_client: PayAdminClient,
    pay_list_payments: Mapping[str, Any],
) -> None:
    try:
        response_get_payment = await pay_admin_client.get_payment(
            payment_id=pay_list_payments["data"][0]["id"],
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_get_payment err: %s", err.response.headers)
        logger.info("response_get_payment body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)

    logger.info(
        "list_payments: %s",
        json.dumps(
            response_get_payment,
            indent=4,
        ),
    )

    assert "https" in response_get_payment["data"]["links"]["self"]
