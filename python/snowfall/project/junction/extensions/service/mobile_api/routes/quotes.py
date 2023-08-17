import lagom
from starlette import endpoints, requests, responses, status

from snowfall.stdlib.integration.starlette import models, request_helpers
from snowfall.vendor.junction.go import client

_DATA_KEY = "data"
_ID_KEY = "id"
_ATTRIBUTES_KEY = "attributes"
_TYPE_KEY = "type"
_DETAILS_KEY = "details"


class OfferQuotes(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_client: client.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        offer_quote = await junction_client.create_offer_quote(
            body["offer"],
            body["options"],
            session_token=request.headers.get("Session-Token"),
        )
        return models.JsonApiResponse(
            models.Body(
                data=models.Resource(**offer_quote[_DATA_KEY]),
            ),
            status.HTTP_201_CREATED,
        )


class OfferQuote(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        junction_client: client.Client = lagom.injectable,
    ) -> responses.Response:
        offer_quote_response = await junction_client.get_offer_quote_by_id(
            request.path_params["offerPriceQuoteId"],
            include=request.scope["parsed_query_string"].get("include", []),
        )
        response_body = models.Body(data=offer_quote_response["data"])

        response_body.included = offer_quote_response.get("included", [])

        return models.JsonApiResponse(response_body)
