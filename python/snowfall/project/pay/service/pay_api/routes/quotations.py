from typing import cast

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.companies.v1alpha import models_pb2 as company_models
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.repositories import (
    CompanyRepository,
    CurrencyRepository,
)
from snowfall.project.pay.service.quotations import quotations
from snowfall.project.pay.service.quotations.quote_calculations import Quote
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.stdlib.money import Currency


class Quotations(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210,WPS211, WPS217
        self,
        request: requests.Request,
        client: currencies.Client = lagom.injectable,
        quotations_repository: quotations.QuotationsRepository = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
        redis_client: UserSessionRepository = lagom.injectable,
        currencies_repository: CurrencyRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        session_token = body.get("externalReference")

        if session_token:
            session_token = session_token + request.user.username

        from_currency = currencies_repository.find_by_id(body["fromCurrency"])
        to_currency = currencies_repository.find_by_id(body["toCurrency"])
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

        from_currency = cast(Currency, from_currency)
        to_currency = cast(Currency, to_currency)
        company = cast(company_models.Company, company)
        beneficiary_company = cast(company_models.Company, beneficiary_company)

        rate = await self._get_rate(
            from_currency,
            to_currency,
            body["amount"],
            session_token,
            redis_client,
            client,
        )

        quote = Quote(
            body["amount"],
            from_currency,
            to_currency,
            rate,
            company,
            beneficiary_company.id,
        )

        quotation = await quotations_repository.insert(quote.to_proto())

        return await messages.create_response(
            body=models.Body(
                data=resources.QuoteResource.from_proto(
                    quotation=quotation,
                    request=request,
                ),
            ),
            request=request,
        )

    async def _get_rate(  # noqa: WPS211
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
        session_token: str | None,
        redis_client: UserSessionRepository,
        currency_client: currencies.Client,
    ) -> float:
        currency_pair = "{0}{1}".format(from_currency.code, to_currency.code)

        rate = None

        if session_token:
            rate = await redis_client.get_rate(session_token, currency_pair)

        if not rate:
            if from_currency == to_currency:
                rate = 1.0
            else:
                response = await currency_client.convert(
                    from_currency,
                    to_currency,
                    amount,
                )
                rate = response.rate

            if session_token:
                await redis_client.store(
                    session_token,
                    currency_pair,
                    rate,
                )

        return rate

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
