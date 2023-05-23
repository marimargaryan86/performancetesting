import json
import logging
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.stdlib import string
from snowfall.vendor.junction.pay.client import Client

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
@pytest.mark.parametrize(
    ("from_currency", "to_currency"),
    [("EUR", "SEK"), ("EUR", "EUR")],
)
async def test_create_transactions(  # noqa: WPS213
    pay_client: Client,
    pay_admin_client: PayAdminClient,
    from_currency: str,
    to_currency: str,
    pay_create_company_payer: Mapping[str, Any],
    pay_create_company_beneficiary: Mapping[str, Any],
) -> None:
    try:
        response_create_quote = await pay_client.create_quote(
            amount=1000,
            external_reference=string.uuid(),
            payer_id=pay_create_company_payer["data"]["id"],
            beneficiary_id=pay_create_company_beneficiary["data"]["id"],
            from_currency=from_currency,
            to_currency=to_currency,
        )
    except httpx.HTTPStatusError as err2:
        logger.info(
            "response_create_quote err:: %s",
            err2.response.headers,
        )
        logger.info("response_create_quote body: %s", err2.response.json())
        pytest.fail(err2.response.json(), pytrace=False)

    logger.info("create_quote: %s", json.dumps(response_create_quote, indent=4))

    external_reference = string.uuid()
    logger.info("external_reference: %s", external_reference)
    invoice_reference = string.uuid()
    logger.info("invoice_reference: %s", invoice_reference)
    logger.info("quotation_id: %s", response_create_quote["data"]["id"])

    try:
        response_create_transactions = await pay_client.create_transactions(
            external_reference=external_reference,
            invoice_reference=invoice_reference,
            quotation_id=response_create_quote["data"]["id"],
        )

    except httpx.HTTPStatusError as err3:
        logger.info("response err:: %s", err3.response.headers)
        logger.info("response_create_transactions body: %s", err3.response.json())
        pytest.fail(err3.response.json(), pytrace=False)

    logger.info(
        "create_transactions: %s",
        json.dumps(response_create_transactions, indent=4),
    )

    rct_data = response_create_transactions["data"]

    if from_currency == to_currency:
        assert rct_data["relationships"]["conversion"] is None
    else:
        assert is_valid_uuid(rct_data["relationships"]["conversion"]["data"]["id"])
        assert rct_data["relationships"]["conversion"]["data"]["type"] == "conversions"
    assert "https" in rct_data["links"]["self"]
