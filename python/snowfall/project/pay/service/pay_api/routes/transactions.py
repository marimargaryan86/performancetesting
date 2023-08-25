import lagom
from starlette import endpoints, requests, status

from snowfall.project.pay.adapter import quotations
from snowfall.project.pay.adapter import transactions as transactions_adapter
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import QuotationStatus
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
    sorting,
)
from snowfall.stdlib.logging import stdout

_logger = stdout.get_logger()


class Transactions(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def post(
        self,
        request: requests.Request,
        quotations_client: quotations.Client = lagom.injectable,
        transactions_client: transactions_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        body = await request_helpers.flatten_request(request)
        quote = await quotations_client.get(identifier=body["quotation"])
        if quote.status == QuotationStatus.QUOTATION_STATUS_QUOTED:
            transaction = await transactions_client.create(
                quotation=quote,
                external_reference=body["externalReference"],
                invoice_reference=body["invoiceReference"],
            )
            await quotations_client.update_status(
                identifier=quote.id,
                status=QuotationStatus.QUOTATION_STATUS_CONFIRMED,
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
        return models.JsonApiResponse(
            body=models.Body(
                errors=[
                    models.Error(
                        status=str(status.HTTP_404_NOT_FOUND),
                        code="not_found",
                        detail="Quotation not valid",
                        source=models.ErrorSourcePointer(
                            pointer="/data/relationships/quotation/data/id",
                        ),
                    ),
                ],
            ),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    async def get(  # noqa: WPS210
        self,
        request: requests.Request,
        client: transactions_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        pagination = pagination_helpers.get_pagination(request)

        sort = sorting.get_sort(request, {"createdAt": "created_at"})
        filter_by = [
            str(uuid)
            for uuid in request.scope["parsed_query_string"].get("filter[ids][eq]", [])
        ]

        response = await client.find(
            limit=pagination.limit or self._default_page_size,
            cursor=pagination.cursor,
            sort=sort,
            filter_by=filter_by,
        )

        data_resources = []
        for transaction in response.transactions:
            try:
                data_resources.append(
                    resources.Transaction.from_proto(transaction, request),
                )
            except Exception:  # noqa: BLE001
                _logger.error(  # noqa: TRY400
                    "data-model is not valid",
                    data=transaction,
                )

        return await messages.create_response(
            body=models.Body(
                data=data_resources,
                links=pagination_helpers.get_next_url(
                    request.url_for("Transactions"),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
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
