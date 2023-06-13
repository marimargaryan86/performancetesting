import json
import logging
from collections.abc import Mapping
from typing import Any

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.vendor.junction.pay.client import Client

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_list_transactions(
    pay_client: Client,
    pay_admin_client: PayAdminClient,
    pay_create_transaction_eur_sek: Mapping[str, Any],
) -> None:
    try:
        response_list_transactions = await pay_admin_client.get_transactions()
    except httpx.HTTPStatusError as err4:
        logger.info("response_list_transactions err:: %s", err4.response.headers)
        logger.info("response_list_transactions body: %s", err4.response.json())
        pytest.fail(err4.response.json(), pytrace=False)

    logger.info(
        "list_transactions: %s",
        json.dumps(
            response_list_transactions,
            indent=4,
        ),
    )

    assert "https" in response_list_transactions["data"][0]["links"]["self"]
    assert "https" in response_list_transactions["links"]["next"]
