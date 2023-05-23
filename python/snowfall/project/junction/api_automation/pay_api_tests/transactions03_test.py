import json
import logging
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.vendor.junction.pay.client import Client

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_get_transaction(
    pay_client: Client,
    pay_admin_client: PayAdminClient,
    pay_create_transaction_eur_sek: Mapping[str, Any],
) -> None:
    try:
        response_get_transaction = await pay_admin_client.get_transaction(
            pay_create_transaction_eur_sek["data"]["id"],
        )
    except httpx.HTTPStatusError as err4:
        logger.info("response_get_transaction err:: %s", err4.response.headers)
        logger.info("response_get_transaction body: %s", err4.response.json())
        pytest.fail(err4.response.json(), pytrace=False)

    logger.info(
        "get_transaction: %s",
        json.dumps(
            response_get_transaction,
            indent=4,
        ),
    )

    assert "https" in response_get_transaction["data"]["links"]["self"]
