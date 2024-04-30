import lagom
from starlette import endpoints, requests, status

from snowfall.project.pay.adapter import transactions as transactions_adapter
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.routes import routes_handlers
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    request_helpers,
)
from snowfall.stdlib.logging import stdout

_logger = stdout.get_logger()


class Transactions(endpoints.HTTPEndpoint):
    _default_page_size = 20

    @routes_handlers.grpc_errors_handler
    async def post(
        self,
        request: requests.Request,
        transactions_client: transactions_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        body = await request_helpers.flatten_request(request)
        transaction = await transactions_client.create(
            quotation_id=body["quotation"],
            external_reference=body["externalReference"],
            invoice_reference=body["invoiceReference"],
            order_id=body["order"],
        )
        return await messages.create_response(
            body=models.Body(
                data=resources.Transaction.from_proto(
                    transaction=transaction,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )


class Transaction(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: transactions_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        transaction = await client.get(request.path_params["transactionId"])
        return await messages.create_response(
            body=models.Body(
                data=resources.Transaction.from_proto(transaction, request),
            ),
            request=request,
        )
