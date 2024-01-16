import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.adapter import resellers
from snowfall.project.junction.go.service.resellers.v1 import models_pb2
from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)


class Resellers(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: resellers.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        response = await client.list_resellers(
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.ResellerResource.from_proto(reseller, request)
                    for reseller in response.resellers
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("Resellers"),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )

    async def post(
        self,
        request: requests.Request,
        client: resellers.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        reseller = await client.create_reseller(
            models_pb2.Reseller(
                name=body["name"],
                company_id=body["company"],
                default_currency=body["currency"],
                provider_ids=body["providers"],
                parent_reseller_ids=body["parentResellers"],
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.ResellerResource.from_proto(
                    reseller=reseller,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )


class Reseller(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: resellers.Client = lagom.injectable,
    ) -> responses.Response:
        reseller = await client.get_reseller(
            request.path_params["resellerId"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.ResellerResource.from_proto(
                    reseller=reseller,
                    request=request,
                ),
            ),
            request=request,
        )

    async def patch(
        self,
        request: requests.Request,
        client: resellers.Client = lagom.injectable,
    ) -> responses.Response:
        reseller_id = request.path_params["resellerId"]
        payload = await request_helpers.flatten_request(request)

        reseller = await client.update_reseller(
            models_pb2.Reseller(
                id=reseller_id,
                name=payload.get("name"),  # type: ignore[arg-type]
                default_currency=payload.get("currency"),  # type: ignore[arg-type]
                provider_ids=payload.get("providers"),
                company_id=payload.get("company"),  # type: ignore[arg-type]
                parent_reseller_ids=payload.get("parentResellers", []),
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.ResellerResource.from_proto(
                    reseller=reseller,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_200_OK,
        )
