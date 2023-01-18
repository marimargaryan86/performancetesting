import currencycloud
import lagom
from starlette import endpoints, requests, responses

from snowfall.project.pay.service.pay_api import pagination_helpers
from snowfall.stdlib import money


class Balances(endpoints.HTTPEndpoint):
    async def get(  # noqa: WPS210
        self,
        request: requests.Request,
        client: currencycloud.Client = lagom.injectable,
    ) -> responses.Response:
        mapped_params = pagination_helpers.map_query_params(
            dict(request.query_params),
            pagination_helpers.PAGINATION_PARAMS_MAPPING,
        )
        balances = client.balances.find(**mapped_params)

        response = []

        next_url = pagination_helpers.get_next_link(
            request.url_for("Balances"),
            balances.pagination,
        )

        for balance in balances:
            price = money.from_string(
                balance.amount,
                money.Currency(balance.currency),
            )
            response.append(
                {
                    "id": balance.id,
                    "type": "balances",
                    "attributes": {
                        "amount": price.amount,
                    },
                    "relationships": {
                        "currency": {
                            "data": {
                                "type": "currencies",
                                "id": balance.currency,
                            },
                        },
                    },
                },
            )

        return responses.JSONResponse({"data": response, "links": next_url})
