import lagom
from starlette import endpoints, requests, status

from snowfall.project.pay.adapter import lead_companies as lead_companies_adapter
from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.project.pay.service.pay_api import resources
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)


class LeadCompany(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        lead_companies_client: lead_companies_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        lead_company_id = request.path_params["leadCompanyId"]
        payload = await request_helpers.flatten_request(request)

        lead_company = await lead_companies_client.update(
            models_pb2.LeadCompany(
                id=lead_company_id,
                name=payload.get("name"),  # type: ignore[arg-type]
                sales_markups=(
                    [
                        money.from_string(
                            str(sales_markup["amount"]),
                            money.Currency(sales_markup["currency"]),
                        ).protobuf()
                        for sales_markup in payload["salesMarkups"]
                    ]
                    if payload.get("salesMarkups")
                    else None
                ),
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.LeadCompany.from_proto(
                    lead_company=lead_company,
                    request=request,
                ),
            ),
            request=request,
        )

    async def get(
        self,
        request: requests.Request,
        lead_companies_client: lead_companies_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        lead_company = await lead_companies_client.get(
            request.path_params["leadCompanyId"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.LeadCompany.from_proto(
                    lead_company=lead_company,
                    request=request,
                ),
            ),
            request=request,
        )


class LeadCompanies(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def post(
        self,
        request: requests.Request,
        lead_companies_client: lead_companies_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        body = await request_helpers.flatten_request(request)

        lead_company = await lead_companies_client.create(
            models_pb2.LeadCompany(
                name=body["name"],
                sales_markups=(
                    [
                        money.from_string(
                            str(sales_markup["amount"]),
                            money.Currency(sales_markup["currency"]),
                        ).protobuf()
                        for sales_markup in body["salesMarkups"]
                    ]
                    if body.get("salesMarkups")
                    else None
                ),
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.LeadCompany.from_proto(
                    lead_company=lead_company,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    async def get(
        self,
        request: requests.Request,
        lead_companies_client: lead_companies_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        pagination = pagination_helpers.get_pagination(request)

        response = await lead_companies_client.find(
            limit=pagination.limit or self._default_page_size,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.LeadCompany.from_proto(
                        lead_company=lead_company,
                        request=request,
                    )
                    for lead_company in response.lead_companies
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("LeadCompanies"),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )
