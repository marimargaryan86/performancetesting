from collections.abc import Mapping
from typing import Any

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.adapter.payments import GrpcClient
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    TransactionRepository,
)
from snowfall.project.pay.service.pay_api.validators import payments_validators
from snowfall.project.pay.service.payments.v1alpha import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    messages,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.logging import stdout

_logger = stdout.get_logger()


class Payment(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        payment_client: GrpcClient = lagom.injectable,
    ) -> responses.Response:
        payment_id = request.path_params["paymentId"]

        payment = await payment_client.get(payment_id)
        if payment is None:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return await messages.create_response(
            body=messages.models.Body(
                data=resources.PaymentsResource.from_models(
                    payment=payment,
                    request=request,
                ),
            ),
            request=request,
        )


class Payments(endpoints.HTTPEndpoint):
    @payments_validators.payment_validator
    async def post(  # noqa: WPS210, WPS211
        self,
        request: requests.Request,
        body: Mapping[str, Any],
        payment_client: GrpcClient = lagom.injectable,
        beneficiaries_repository: BeneficiaryRepository = lagom.injectable,
        transaction_repository: TransactionRepository = lagom.injectable,
    ) -> responses.Response:
        original_body = await request_helpers.flatten_request(request)
        amount, beneficiary, transaction_models, payment_at = (
            body.get("amount"),
            body["beneficiary"],
            body.get("transactions", []),
            body["paymentAt"],
        )
        total_amount = (
            money.total(
                (
                    money.from_protobuf(tm.amounts.beneficiary)
                    for tm in transaction_models
                ),
            )
            if amount is None
            else money.Money(
                amount=amount,
                currency=money.Currency(
                    beneficiary.currency,
                ),
            )
        )

        payment = await payment_client.create(
            models_pb2.Payment(
                amount=total_amount.protobuf(),
                beneficiary_id=beneficiary.external_reference,
                reason=body["reason"],
                reference=body["reference"],
                payment_type=beneficiary.payment_type,
                payment_due_date=protobuf.date_to_protobuf(
                    payment_at,
                ),
                transactions=original_body.get("transactions", []),
            ),
        )

        return await messages.create_response(
            body=messages.models.Body(
                data=resources.PaymentsResource.from_models(
                    payment=payment,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    async def get(
        self,
        request: requests.Request,
        payment_client: GrpcClient = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)

        payments = await payment_client.find(
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        response_data = [
            resources.PaymentsResource.from_models(
                payment=payment,
                request=request,
            )
            for payment in payments.payments
        ]
        return await messages.create_response(
            body=messages.models.Body(
                data=response_data,
                links=pagination_helpers.get_next_url(
                    request.url_for("Payments"),
                    payments.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )
