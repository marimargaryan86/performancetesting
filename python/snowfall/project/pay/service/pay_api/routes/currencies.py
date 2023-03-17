import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import CurrencyRepository
from snowfall.stdlib import sequence
from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers


class Currencies(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        currencies_repository: CurrencyRepository = lagom.injectable,
    ) -> responses.Response:
        currency_id = request.path_params["currencyId"]
        currency = currencies_repository.find_by_id(currency_id)
        if currency is None:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return await messages.create_response(
            body=models.Body(
                data=resources.CurrenciesResource.from_model(
                    currency,
                    request,
                ),
            ),
            request=request,
        )


class ListCurrencies(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        currencies_repository: CurrencyRepository = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        all_currencies = currencies_repository.find()

        sorted_currencies = sorted(
            all_currencies,
            key=lambda curr: curr.code,
        )

        sequence_currencies = sequence.paginate(
            sequence=sorted_currencies,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=messages.models.Body(
                data=[
                    resources.CurrenciesResource.from_model(
                        currency,
                        request,
                    )
                    for currency in sequence_currencies.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "Currencies",
                    ),
                    sequence_currencies.cursor,
                    pagination,
                ),
            ),
            request=request,
        )
