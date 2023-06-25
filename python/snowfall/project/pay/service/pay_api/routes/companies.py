import lagom
from starlette import endpoints, requests, status

from snowfall.project.pay.adapter import companies as companies_adapter
from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.project.pay.service.pay_api import resources
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.v1 import postal_address_pb2


class AdminCompany(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        companies_client: companies_adapter.GrpcClient = lagom.injectable,
    ) -> models.JsonApiResponse:
        company_id = request.path_params["companyId"]
        payload = await request_helpers.flatten_request(request)

        address = payload.get("address", {})
        company = await companies_client.update(
            models_pb2.Company(
                id=company_id,
                name=payload.get("name"),  # type: ignore[arg-type]
                address=postal_address_pb2.PostalAddress(
                    address_lines=address.get("addressLines"),
                    region_code=address.get("countryCode"),
                    postal_code=address.get("postalCode"),
                    locality=address.get("city"),
                ),
                fx_markup=payload.get("fxMarkup"),  # type: ignore[arg-type]
                processing_markup=payload.get("processingMarkup"),  # type: ignore[arg-type]
                sales_markup=payload.get("salesMarkup"),  # type: ignore[arg-type]
            ),
        )

        return await messages.create_response(
            body=messages.models.Body(
                data=resources.Company.from_proto(
                    company=company,
                    request=request,
                ),
            ),
            request=request,
        )

    async def get(
        self,
        request: requests.Request,
        companies_client: companies_adapter.GrpcClient = lagom.injectable,
    ) -> models.JsonApiResponse:
        company = await companies_client.get(request.path_params["companyId"])

        return await messages.create_response(
            body=messages.models.Body(
                data=resources.Company.from_proto(
                    company=company,
                    request=request,
                ),
            ),
            request=request,
        )


class AdminCompanies(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def post(
        self,
        request: requests.Request,
        companies_client: companies_adapter.GrpcClient = lagom.injectable,
    ) -> models.JsonApiResponse:
        body = await request_helpers.flatten_request(request)
        address = body["address"]

        company = await companies_client.create(
            models_pb2.Company(
                name=body["name"],
                address=postal_address_pb2.PostalAddress(
                    address_lines=address["addressLines"],
                    region_code=address["countryCode"],
                    postal_code=address["postalCode"],
                    locality=address["city"],
                    revision=0,
                ),
                fx_markup=float(body["fxMarkup"]),
                processing_markup=float(body["processingMarkup"]),
                sales_markup=float(body["salesMarkup"]),
            ),
        )

        return await messages.create_response(
            body=messages.models.Body(
                data=resources.Company.from_proto(
                    company=company,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    async def get(
        self,
        request: requests.Request,
        companies_client: companies_adapter.GrpcClient = lagom.injectable,
    ) -> models.JsonApiResponse:
        pagination = pagination_helpers.get_pagination(request)

        response = await companies_client.find(
            limit=pagination.limit or self._default_page_size,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.Company.from_proto(
                        company=company,
                        request=request,
                    )
                    for company in response.companies
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("Companies"),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )


class AdminAccountlessCompanies(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def get(
        self,
        request: requests.Request,
        companies_client: companies_adapter.GrpcClient = lagom.injectable,
    ) -> models.JsonApiResponse:
        pagination = pagination_helpers.get_pagination(request)

        response = await companies_client.find_accountless(
            limit=pagination.limit or self._default_page_size,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.Company.from_proto(
                        company=company,
                        request=request,
                    )
                    for company in response.companies
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("AccountlessCompanies"),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )
