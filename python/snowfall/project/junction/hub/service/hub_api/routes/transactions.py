import lagom
from starlette import endpoints, requests

from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.junction.hub.service.hub_api.permissions import check_permission
from snowfall.project.pay.adapter import transactions as transactions_adapter
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    sorting,
)
from snowfall.stdlib.logging import stdout

_logger = stdout.get_logger()


class Transactions(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def get(
        self,
        request: requests.Request,
        client: transactions_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("pay.view", request.user.permissions)

        pagination = pagination_helpers.get_pagination(request)

        sort = sorting.get_sort(request, {"createdAt": "created_at"})
        filter_by = [
            str(uuid)
            for uuid in request.scope["parsed_query_string"].get("filter[ids][eq]", [])
        ]
        filter_by_bill_ids = [
            str(uuid)
            for uuid in request.scope["parsed_query_string"].get(
                "filter[bill.id][eq]",
                [],
            )
        ]
        filter_by_external_reference = [
            str(uuid)
            for uuid in request.scope["parsed_query_string"].get(
                "filter[externalReference][eq]",
                [],
            )
        ]

        response = await client.find(
            limit=pagination.limit or self._default_page_size,
            cursor=pagination.cursor,
            sort=sort,
            filter_by=filter_by,
            filter_by_bill_ids=filter_by_bill_ids,
            filter_by_external_reference=filter_by_external_reference,
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
        check_permission("pay.view", request.user.permissions)

        transaction = await client.get(request.path_params["transactionId"])
        return await messages.create_response(
            body=models.Body(
                data=resources.Transaction.from_proto(transaction, request),
            ),
            request=request,
        )
