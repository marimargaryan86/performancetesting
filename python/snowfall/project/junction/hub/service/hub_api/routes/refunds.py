import lagom
from starlette import endpoints, requests, status

from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.junction.hub.service.hub_api.permissions import check_permission
from snowfall.project.junction.hub.service.hub_api.routes import routes_handlers
from snowfall.project.pay.adapter import (
    refunds as refunds_adapter,
)
from snowfall.project.pay.adapter import (
    transactions as transactions_adapter,
)
from snowfall.project.pay.service.refunds.v1 import models_pb2 as refunds_model_pb2
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)


class Refund(endpoints.HTTPEndpoint):
    @routes_handlers.grpc_errors_handler
    async def patch(
        self,
        request: requests.Request,
        refunds_client: refunds_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("refund.edit", request.user.permissions)

        refund_id = request.path_params["refundId"]
        payload = await request_helpers.flatten_request(request)

        refund = await refunds_client.update(
            refunds_model_pb2.Refund(
                id=refund_id,
                note=payload.get("note"),  # type: ignore[arg-type]
                refunded_us=(
                    money.from_string(
                        str(payload["refundedUs"]["amount"]),
                        money.Currency(payload["refundedUs"]["currency"]),
                    ).protobuf()
                    if payload.get("refundedUs")
                    else None
                ),
                refunded_reseller=(
                    money.from_string(
                        str(payload["refundedReseller"]["amount"]),
                        money.Currency(payload["refundedReseller"]["currency"]),
                    ).protobuf()
                    if payload.get("refundedReseller")
                    else None
                ),
                invoice_reference=payload.get("invoiceReference"),  # type: ignore[arg-type]
                external_reference_id=payload.get("externalReference"),  # type: ignore[arg-type]
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.RefundsResource.from_proto(
                    refund=refund,
                    request=request,
                ),
            ),
            request=request,
        )

    async def get(
        self,
        request: requests.Request,
        refunds_client: refunds_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("refund.view", request.user.permissions)

        refund = await refunds_client.get(request.path_params["refundId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.RefundsResource.from_proto(
                    refund=refund,
                    request=request,
                ),
            ),
            request=request,
        )


class Refunds(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def get(
        self,
        request: requests.Request,
        refunds_client: refunds_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("refund.view", request.user.permissions)

        pagination = pagination_helpers.get_pagination(request)

        response = await refunds_client.find(
            limit=pagination.limit or self._default_page_size,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.RefundsResource.from_proto(
                        refund=refund,
                        request=request,
                    )
                    for refund in response.refunds
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("Refunds"),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )

    @routes_handlers.grpc_errors_handler
    async def post(
        self,
        request: requests.Request,
        refunds_client: refunds_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("refund.add", request.user.permissions)

        payload = await request_helpers.flatten_request(request)
        refund = await refunds_client.create(
            refunds_model_pb2.Refund(
                refund_received=payload["refundReceived"],
                note=payload["note"],
                refunded_us=money.Money(
                    payload["refundedUs"]["amount"],
                    money.Currency(payload["refundedUs"]["currency"]),
                ).protobuf(),
                refunded_reseller=money.Money(
                    payload["refundedReseller"]["amount"],
                    money.Currency(payload["refundedReseller"]["currency"]),
                ).protobuf(),
                invoice_reference=payload["invoiceReference"],
                transaction_id=payload["transaction"],
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.RefundsResource.from_proto(
                    refund=refund,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )


class RefundPosition(endpoints.HTTPEndpoint):
    @routes_handlers.grpc_errors_handler
    async def post(
        self,
        request: requests.Request,
        refunds_client: refunds_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("refund.edit", request.user.permissions)

        refund_id = request.path_params["refundId"]
        body = await request_helpers.flatten_request(request)

        calculated_refund_position = await refunds_client.calculate_refund_position(
            refund_id,
            money.Money(
                body["refundedUs"]["amount"],
                money.Currency(body["refundedUs"]["currency"]),
            ),
            money.Money(
                body["refundedReseller"]["amount"],
                money.Currency(
                    body["refundedReseller"]["currency"],
                ),
            ),
        )
        return await messages.create_response(
            body=models.Body(
                data=resources.RefundPosition.from_models(
                    refund_id,
                    calculated_refund_position,
                ),
            ),
            request=request,
        )


class RefundByBooking(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        transactions_client: transactions_adapter.Client = lagom.injectable,
        refunds_client: refunds_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("refund.view", request.user.permissions)

        transaction = await transactions_client.get(
            request.path_params["bookingId"],
            selector="external_reference_id",
        )
        refund = await refunds_client.get(
            transaction.id,
            selector="transaction_id",
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.RefundsResource.from_proto(
                    refund=refund,
                    request=request,
                ),
            ),
            request=request,
        )
