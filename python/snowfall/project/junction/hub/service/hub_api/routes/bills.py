import lagom
from starlette import endpoints, requests

from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.junction.hub.service.hub_api.permissions import check_permission
from snowfall.project.pay.adapter import bills as bills_adapter
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
    sorting,
)


class Bill(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        bills_client: bills_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("bill.edit", request.user.permissions)

        bill_id = request.path_params["billId"]
        payload = await request_helpers.flatten_request(request)
        bill = await bills_client.update_reconciliation(
            identifier=bill_id,
            is_reconciled=payload["isReconciled"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.BillResource.from_proto(
                    bill=bill,
                    request=request,
                ),
            ),
            request=request,
        )

    async def get(
        self,
        request: requests.Request,
        bills_client: bills_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("bill.view", request.user.permissions)

        bill = await bills_client.get(request.path_params["billId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.BillResource.from_proto(
                    bill=bill,
                    request=request,
                ),
            ),
            request=request,
        )


class Bills(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def get(
        self,
        request: requests.Request,
        bills_client: bills_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("bill.view", request.user.permissions)

        pagination = pagination_helpers.get_pagination(request)
        sort = sorting.get_sort(request, {"updatedAt": "updated_at"})
        response = await bills_client.find(
            limit=pagination.limit or self._default_page_size,
            cursor=pagination.cursor,
            sort=sort,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.BillResource.from_proto(
                        bill=bill,
                        request=request,
                    )
                    for bill in response.bills
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("Bills"),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )
