import json
import logging
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_create_payment(
    pay_admin_client: PayAdminClient,
    pay_create_company_beneficiary: Mapping[str, Any],
    pay_create_transaction_eur_sek: Mapping[str, Any],
    pay_create_transaction_sek_eur: Mapping[str, Any],
) -> None:
    logger.info("eur_sek: %s", json.dumps(pay_create_transaction_eur_sek, indent=4))
    logger.info("sek_eur: %s", json.dumps(pay_create_transaction_sek_eur, indent=4))
    try:
        response_create_payment = await pay_admin_client.create_payment(
            amount=1000,
            reason="Payment for API test purposes",
            reference="Reference for API test purposes",
            payment_at="2023-01-01T00:00:00+00:00",
            beneficiary_id=pay_create_company_beneficiary["data"]["id"],
            transactions_ids=[
                pay_create_transaction_eur_sek["data"]["id"],
                pay_create_transaction_sek_eur["data"]["id"],
            ],
        )
    except httpx.HTTPStatusError as err:
        logger.info(
            "response_create_payment err: %s",
            err.response.headers,
        )
        logger.info("response_create_payment body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)

    logger.info("create_payment: %s", json.dumps(response_create_payment, indent=4))
    assert "https" in response_create_payment["links"]["self"]
