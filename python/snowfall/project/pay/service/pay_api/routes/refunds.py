import lagom
from starlette import endpoints, requests

from snowfall.project.pay.adapter import refunds as refunds_adapter
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.routes import routes_handlers
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
        refund_id = request.path_params["refundId"]
        payload = await request_helpers.flatten_request(request)

        refund = await refunds_client.update(
            identifier=refund_id,
            refunded_by_provider=money.from_string(
                str(payload["refundedUs"]["amount"]),
                money.Currency(payload["refundedUs"]["currency"]),
            ).protobuf(),
            refunded_to_reseller=money.from_string(
                str(payload["refundedReseller"]["amount"]),
                money.Currency(payload["refundedReseller"]["currency"]),
            ).protobuf(),
            invoice_reference=payload["invoiceReference"],
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


class RefundPosition(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        refunds_client: refunds_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
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
