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
async def test_list_payments(
    pay_admin_client: PayAdminClient,
) -> None:
    try:
        response_list_payments = await pay_admin_client.list_payments()
    except httpx.HTTPStatusError as err:
        logger.info("response_list_payments err: %s", err.response.headers)
        logger.info("response_list_payments body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)

    logger.info(
        "list_payments: %s",
        json.dumps(
            response_list_payments,
            indent=4,
        ),
    )

    assert "https" in response_list_payments["data"][0]["links"]["self"]
    assert "https" in response_list_payments["links"]["next"]
