import datetime
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
async def test_create_payment_amount_transactions(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
    pay_create_beneficiary: Mapping[str, Any],
    pay_create_transaction_eur_sek: Mapping[str, Any],
    pay_create_transaction_eur_usd: Mapping[str, Any],
) -> None:
    logger.info("eur_sek: %s", json.dumps(pay_create_transaction_eur_sek, indent=4))
    logger.info("eur_usd: %s", json.dumps(pay_create_transaction_eur_usd, indent=4))
    with pytest.raises(httpx.HTTPStatusError) as err:
        await pay_admin_client.create_payment(
            amount=1000,
            reason="Payment for API test purposes",
            reference="Reference for API test purposes",
            payment_at=str(
                (
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
                ).date(),
            ),
            beneficiary_id=pay_create_beneficiary["data"]["id"],
            transactions_ids=[
                pay_create_transaction_eur_sek["data"]["id"],
                pay_create_transaction_eur_usd["data"]["id"],
            ],
        )
    error = err.value  # noqa: WPS441

    logger.info("response_create_payment err headers: %s", error.response.headers)
    logger.info("response_create_payment body: %s", error.response.json())

    first_error = error.response.json()["errors"][0]
    assert first_error["status"] == "400"
    assert first_error["code"] == "bad_request"
    assert first_error["detail"] == "Need to provide amount or transactions"
    assert first_error["source"]["pointer"] == "/data/relationships/transactions"
    second_error = error.response.json()["errors"][1]
    assert second_error["status"] == "400"
    assert second_error["code"] == "bad_request"
    assert second_error["detail"] == "Need to provide amount or transactions"
    assert second_error["source"]["pointer"] == "/data/attributes/amount"


@pytest.mark.integration()
async def test_create_payment_amount(
    pay_admin_client: PayAdminClient,
    pay_create_beneficiary: Mapping[str, Any],
) -> None:
    try:
        response_create_payment = await pay_admin_client.create_payment(
            amount=1000,
            reason="Payment for API test purposes",
            reference="Reference for API test purposes",
            payment_at=str(
                (
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
                ).date(),
            ),
            beneficiary_id=pay_create_beneficiary["data"]["id"],
            transactions_ids=[],
        )
    except httpx.HTTPStatusError as err:
        logger.info(
            "response_create_payment err: %s",
            err.response.headers,
        )
        logger.info("response_create_payment body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info("create_payment: %s", json.dumps(response_create_payment, indent=4))
    assert "https" in response_create_payment["data"]["links"]["self"]


@pytest.mark.integration()
async def test_create_payment_transactions(
    pay_admin_client: PayAdminClient,
    pay_create_beneficiary: Mapping[str, Any],
    pay_create_transaction_eur_sek: Mapping[str, Any],
) -> None:
    logger.info("eur_sek: %s", json.dumps(pay_create_transaction_eur_sek, indent=4))
    try:
        response_create_payment = await pay_admin_client.create_payment(
            reason="Payment for API test purposes",
            reference="Reference for API test purposes",
            payment_at=str(
                (
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
                ).date(),
            ),
            beneficiary_id=pay_create_beneficiary["data"]["id"],
            transactions_ids=[
                pay_create_transaction_eur_sek["data"]["id"],
            ],
        )
    except httpx.HTTPStatusError as err:
        logger.info(
            "response_create_payment err: %s",
            err.response.headers,
        )
        logger.info("response_create_payment body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info("create_payment: %s", json.dumps(response_create_payment, indent=4))
    assert "https" in response_create_payment["data"]["links"]["self"]
