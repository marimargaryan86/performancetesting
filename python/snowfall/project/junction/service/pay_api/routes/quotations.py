import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.adapter import currencies
from snowfall.project.junction.service.pay_api import resources
from snowfall.project.junction.service.pay_api.repositories import CompanyRepository
from snowfall.project.pay.service.quotations import quotations
from snowfall.project.pay.service.quotations.quote_calculations import Quote
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.stdlib.money import Currency


class Quotations(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210
        self,
        request: requests.Request,
        client: currencies.Client = lagom.injectable,
        quotations_repository: quotations.QuotationsRepository = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        from_currency, to_currency = Currency(body["fromCurrency"]), Currency(
            body["toCurrency"],
        )
        if from_currency == to_currency:
            rate = 1.0
        else:
            rate = await client.get_rate(
                from_currency,
                to_currency,
                body["amount"],
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
