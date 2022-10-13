import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.adapter import currencies
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import request_helpers

_DATA_KEY = "data"
_CONVERSION_AMOUNT = 1000


class Rates(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        client: currencies.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        rate = await client.get_rate(
            body["fromCurrency"],
            body["toCurrency"],
            _CONVERSION_AMOUNT,
        )

        payload = {
            _DATA_KEY: {
                "type": "rates",
                "id": string.uuid(),
                "attributes": {
                    "rate": float(rate),
                },
                "relationships": {
                    "fromCurrency": {
                        _DATA_KEY: {"id": body["fromCurrency"], "type": "currencies"},
                    },
                    "toCurrency": {
                        _DATA_KEY: {"id": body["toCurrency"], "type": "currencies"},
                    },
                },
            },
        }
        return responses.JSONResponse(payload)
