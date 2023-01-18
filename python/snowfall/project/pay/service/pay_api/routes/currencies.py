from starlette import endpoints, exceptions, requests, responses, status

from snowfall.stdlib import money


class Currencies(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        currency_id = request.path_params["currencyId"]

        try:
            currency = money.Currency(currency_id)
        except ValueError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        currency_details = {
            "id": currency_id,
            "type": "currencies",
            "attributes": {"name": currency.currency_name},
        }

        return responses.JSONResponse({"data": currency_details})
