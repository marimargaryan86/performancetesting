import datetime
import json
import logging
from collections.abc import Mapping
from typing import Any

import grpc
import httpx
import pytest
from google.protobuf.json_format import MessageToDict

from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.project.junction.api_automation.test_functions.pay_webhook_client import (
    PayWebhookClient,
)
from snowfall.project.pay.service.payments.v1alpha import (
    payments_pb2,
    payments_pb2_grpc,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_webhook_create_payment_amount(  # noqa: WPS210
    pay_admin_client: PayAdminClient,
    pay_webhook_client: PayWebhookClient,
    pay_create_beneficiary: Mapping[str, Any],
    pay_webhook_secret_key: str,
    grpc_payment_service_stub: payments_pb2_grpc.PaymentsServiceStub,
) -> None:
    expected_status = "completed"
    amount = 1000
    pcbd = pay_create_beneficiary["data"]
    currency_id = pcbd["relationships"]["currency"]["data"]["id"]
    pay_date = datetime.datetime.now(tz=datetime.UTC)
    payment_date = str(pay_date.date())
    pay_date_str = str(pay_date)

    beneficiary_id = pay_create_beneficiary["data"]["id"]
    reason = "Payment for API test purposes"

    response_create_payment = await create_payment_response(
        amount,
        beneficiary_id,
        pay_admin_client,
        payment_date,
        reason,
    )
    logger.info("create_payment: %s", json.dumps(response_create_payment, indent=4))

    external_reference_id = await get_external_reference_id(
        grpc_payment_service_stub,
        response_create_payment["data"]["id"],
    )

    response = await pay_webhook_client.trigger_payment_webhook(
        str(amount),
        beneficiary_id,
        currency_id,
        pay_date_str,
        reason,
        external_reference_id,
        expected_status,
        pay_webhook_secret_key,
    )
    logger.info("webhook_response: %s", response)

    response_get_payment = await pay_admin_client.get_payment(
        response_create_payment["data"]["id"],
    )
    logger.info("get_payment: %s", json.dumps(response_get_payment, indent=4))

    assert response_get_payment["data"]["attributes"]["status"] == expected_status


async def create_payment_response(
    amount: int,
    beneficiary_id: str,
    pay_admin_client: PayAdminClient,
    payment_date: str,
    reason: str,
) -> dict[str, Any]:
    try:
        response_create_payment = await pay_admin_client.create_payment(
            amount=amount,
            reason=reason,
            reference="Reference for API test purposes",
            payment_at=payment_date,
            beneficiary_id=beneficiary_id,
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

    return response_create_payment


async def get_external_reference_id(
    grpc_payment_stub: payments_pb2_grpc.PaymentsServiceStub,
    payment_id: str,
) -> str:
    get_payment_request = payments_pb2.GetPaymentRequest(
        id=payment_id,
    )
    try:
        response = await grpc_payment_stub.GetPayment(get_payment_request)
    except grpc.aio.AioRpcError as err:
        metadata_err = str(err.trailing_metadata())
        pytest.fail(metadata_err, pytrace=False)

    logger.info("get_payment: %s", response)
    assert response
    json_response = MessageToDict(response)

    return json_response["payment"]["externalReferenceId"]
