from typing import cast

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.pay.adapter import currencies, quotations
from snowfall.project.pay.service.companies.v1alpha import models_pb2 as company_models
from snowfall.project.pay.service.currencies.v1alpha.models_pb2 import Currency
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import CompanyRepository
from snowfall.stdlib.integration.starlette import messages, models, request_helpers


class Quotations(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210,WPS211, WPS217
        self,
        request: requests.Request,
        quotations_client: quotations.Client = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
        currency_client: currencies.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        session_token = body.get("externalReference")

        if session_token:
            session_token = session_token + request.user.username
        from_currency = await currency_client.get(
            body["fromCurrency"],
            no_exist_ok=True,
        )
        to_currency = await currency_client.get(body["toCurrency"], no_exist_ok=True)
        company = await companies_repository.find_by_id(body["payer"])
        beneficiary_company = await companies_repository.find_by_id(body["beneficiary"])
        errors = self._validate(
            from_currency,
            to_currency,
            company,
            beneficiary_company,
        )

        if errors:
            return models.JsonApiResponse(
                body=messages.models.Body(
                    errors=errors,
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        company = cast(company_models.Company, company)
        beneficiary_company = cast(company_models.Company, beneficiary_company)

        quotation = await quotations_client.create(
            from_currency=body["fromCurrency"],
            to_currency=body["toCurrency"],
            amount=body["amount"],
            payer=company,
            beneficiary_company=beneficiary_company,
            session_token=session_token,
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.QuoteResource.from_proto(
                    quotation=quotation,
                    request=request,
                ),
            ),
            request=request,
        )

    def _validate(
        self,
        from_currency: Currency | None,
        to_currency: Currency | None,
        company: company_models.Company | None,
        beneficiary_company: company_models.Company | None,
    ) -> list[messages.models.Error]:
        errors = []
        if not from_currency:
            errors.append(
                messages.models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="Provided currency is not supported",
                    source=messages.models.ErrorSourcePointer(
                        pointer="data/relationships/fromCurrency",
                    ),
                ),
            )
        if not to_currency:
            errors.append(
                messages.models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="Provided currency is not supported",
                    source=messages.models.ErrorSourcePointer(
                        pointer="data/relationships/toCurrency",
                    ),
                ),
            )

        if not company:
            errors.append(
                messages.models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="Provided company not found",
                    source=messages.models.ErrorSourcePointer(
                        pointer="data/relationships/payer",
                    ),
                ),
            )

        if not beneficiary_company:
            errors.append(
                messages.models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="Provided company not found",
                    source=messages.models.ErrorSourcePointer(
                        pointer="data/relationships/beneficiary",
                    ),
                ),
            )
        return errors
