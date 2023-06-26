import lagom
from starlette import endpoints, requests, responses

from snowfall.project.pay.adapter.currencies import Client
from snowfall.project.pay.service.pay_api import resources
from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers


class Currencies(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        currencies_client: Client = lagom.injectable,
    ) -> responses.Response:
        currency_id = request.path_params["currencyId"]
        currency = await currencies_client.get(currency_id)
        return await messages.create_response(
            body=models.Body(
                data=resources.CurrenciesResource.from_model(
                    currency,  # type: ignore[arg-type]
                    request,
                ),
            ),
            request=request,
        )


class ListCurrencies(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        currencies_client: Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        currencies_page = await currencies_client.find(
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
                    for currency in currencies_page.currencies
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "Currencies",
                    ),
                    currencies_page.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )
