import lagom
from starlette import endpoints, requests, status

from snowfall.project.pay.adapter import refunds as refunds_adapter
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.routes import routes_handlers
from snowfall.project.pay.service.refunds.v1alpha import models_pb2
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

    @routes_handlers.grpc_errors_handler
    async def post(
        self,
        request: requests.Request,
        refunds_client: refunds_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        payload = await request_helpers.flatten_request(request)

        refund = await refunds_client.create(
            models_pb2.Refund(
                transaction_id=payload.get("transaction"),  # type: ignore[arg-type]
                refund_received=payload.get("refundReceived"),  # type: ignore[arg-type]
                note=payload.get("note"),  # type: ignore[arg-type]
                refunded_us=money.from_string(
                    str(payload["refundedUs"]["amount"]),
                    money.Currency(payload["refundedUs"]["currency"]),
                ).protobuf(),
                refunded_reseller=money.from_string(
                    str(payload["refundedReseller"]["amount"]),
                    money.Currency(payload["refundedReseller"]["currency"]),
                ).protobuf(),
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
