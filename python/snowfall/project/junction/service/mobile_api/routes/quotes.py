import decimal
from typing import Optional

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.service.mobile_api import repository, validators
from snowfall.project.junction.service.mobile_api.models.cached_rate import CachedRate
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import models, request_helpers
from snowfall.vendor.junction import client

_DATA_KEY = "data"
_ID_KEY = "id"
_ATTRIBUTES_KEY = "attributes"
_TYPE_KEY = "type"
_DETAILS_KEY = "details"


class OfferQuotes(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_client: client.JunctionClient = lagom.injectable,
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
    @validators.get_session_token_rates
    async def get(
        self,
        request: requests.Request,
        cached_rate: Optional[CachedRate],
        junction_client: client.JunctionClient = lagom.injectable,
        offers_rates_repository: repository.OffersRatesRepository = lagom.injectable,
    ) -> responses.Response:
        offer_quote_response = await junction_client.get_offer_quote_by_id(
            request.path_params["offerPriceQuoteId"],
        )
        attributes = offer_quote_response[_DATA_KEY][_ATTRIBUTES_KEY]
        if cached_rate and attributes["status"] == "completed":
            attributes_price_currency = attributes["price"]["currency"]
            if cached_rate.currency != attributes_price_currency:
                new_money = money.from_string(
                    attributes["price"]["amount"],
                    money.Currency(
                        attributes_price_currency,
                    ),
                ).convert(
                    money.Currency(cached_rate.currency),
                    decimal.Decimal(cached_rate.rate),
                )
                attributes["price"]["amount"] = str(
                    new_money,
                )
                attributes["price"]["currency"] = cached_rate.currency
        return models.JsonApiResponse(models.Body(data=offer_quote_response["data"]))
