from typing import Any, Mapping

import lagom
from starlette import endpoints, exceptions, requests, status

from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import CompanyRepository
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.v1 import postal_address_pb2


def _update_company_from_payload(
    company: models_pb2.Company,
    payload: Mapping[str, Any],
) -> models_pb2.Company:
    address = payload.get("address", {})
    return models_pb2.Company(
        id=company.id,
        name=payload.get("name", company.name),
        address=postal_address_pb2.PostalAddress(
            address_lines=address.get("addressLines", company.address.address_lines),
            region_code=address.get("countryCode", company.address.region_code),
            postal_code=address.get("postalCode", company.address.postal_code),
            locality=address.get("city", company.address.locality),
        ),
        fx_markup=payload.get("fxMarkup", company.fx_markup),
        processing_markup=payload.get("processingMarkup", company.processing_markup),
        sales_markup=payload.get("salesMarkup", company.sales_markup),
    )


class AdminCompany(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        company_repository: CompanyRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        company_id = request.path_params["companyId"]
        body = await request_helpers.flatten_request(request)

        company = await company_repository.find_by_id(company_id)

        if not company:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        company = _update_company_from_payload(company, body)

        await company_repository.update(
            company_id,
            company,
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
        company_repository: CompanyRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        company_id = request.path_params["companyId"]

        company = await company_repository.find_by_id(company_id)
        if not company:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

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
        companies_repository: CompanyRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        body = await request_helpers.flatten_request(request)
        address = body["address"]
        company = await companies_repository.insert(
            models_pb2.Company(
                id=string.uuid(),
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
        company_repository: CompanyRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        pagination = pagination_helpers.get_pagination(request)

        companies = await company_repository.find(
            cursor=pagination.cursor,
        )

        companies.limit(pagination.limit or self._default_page_size)

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.Company.from_proto(
                        company=company,
                        request=request,
                    )
                    async for company in companies
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("Companies"),
                    await companies.cursor(),
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
        company_repository: CompanyRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        pagination = pagination_helpers.get_pagination(request)

        companies = await company_repository.find(
            cursor=pagination.cursor,
            filter_={"account_id": ""},
        )

        companies.limit(pagination.limit or self._default_page_size)

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.Company.from_proto(
                        company=company,
                        request=request,
                    )
                    async for company in companies
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("AccountlessCompanies"),
                    await companies.cursor(),
                    pagination,
                ),
            ),
            request=request,
        )
