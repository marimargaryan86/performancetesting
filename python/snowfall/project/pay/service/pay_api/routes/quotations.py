import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.repositories import CompanyRepository
from snowfall.project.pay.service.quotations import quotations
from snowfall.project.pay.service.quotations.quote_calculations import Quote
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.stdlib.money import Currency


class Quotations(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210,WPS211
        self,
        request: requests.Request,
        client: currencies.Client = lagom.injectable,
        quotations_repository: quotations.QuotationsRepository = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
        redis_client: UserSessionRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        session_token = body.get("externalReference")

        if session_token:
            session_token = session_token + request.user.username
        from_currency, to_currency = Currency(body["fromCurrency"]), Currency(
            body["toCurrency"],
        )

        rate = await self._get_rate(
            from_currency,
            to_currency,
            body["amount"],
            session_token,
            redis_client,
            client,
        )

        company = await companies_repository.find_by_id(body["payer"])

        if not company:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        quote = Quote(
            body["amount"],
            from_currency,
            to_currency,
            rate,
            company,
            body["beneficiary"],
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
