import datetime
import decimal
import json
import re

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.adapter import errors
from snowfall.project.junction.extensions.service.mobile_api import (
    currencies,
    repository,
    validators,
)
from snowfall.project.junction.extensions.service.mobile_api.models.cached_rate import (
    CachedRate,
)
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import (
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.vendor.junction import client

_DATA_KEY = "data"
_ID_KEY = "id"
_ATTRIBUTES_KEY = "attributes"
_TYPE_KEY = "type"
_DETAILS_KEY = "details"


class OfferSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_client: client.JunctionClient = lagom.injectable,
        offers_rates_repository: repository.OffersRatesRepository = lagom.injectable,
        currencies_client: currencies.CurrencyClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        if body.get("currency"):
            try:
                rate = await currencies_client.get_rate(
                    "EUR",  # type: ignore[arg-type]
                    body["currency"],
                    currencies_client.get_ttl_hash(),  # type: ignore[arg-type]
                )
            except errors.NotFoundError as exc:
                return models.JsonApiResponse(
                    models.Body(
                        errors=[
                            models.Error(
                                status=str(status.HTTP_400_BAD_REQUEST),
                                code="unsupported_currency",
                                detail=exc.args[0],
                            ),
                        ],
                    ),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            await offers_rates_repository.create(
                # TODO: This will not work with multiple currencies simultaneously
                identifier=request.headers.get("Session-Token", ""),
                atr_value=json.dumps({"rate": rate, "currency": body["currency"]}),
            )
        offer_search = await junction_client.create_offer_search(
            trip_ids=body["trips"],
            passengers_dates_of_birth=[
                datetime.date.fromisoformat(passenger["dateOfBirth"])
                for passenger in body["passengers"]
            ],
            session_token=request.headers.get("Session-Token"),
        )
        return models.JsonApiResponse(
            models.Body(
                data=models.Resource(**offer_search[_DATA_KEY]),
            ),
            status.HTTP_201_CREATED,
        )


class OfferSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        offer_search = await junction_client.get_offer_search(
            offers_search_id=request.path_params["offerSearchId"],
            include=request.scope["query_string"].get(
                "include",
                [],
            ),
        )
        response_body = models.Body(data=offer_search["data"])
        if offer_search.get("included"):
            response_body.included = offer_search.get("included")
        return models.JsonApiResponse(response_body)


class OffersByOfferSearch(endpoints.HTTPEndpoint):
    @validators.get_session_token_rates
    async def get(  # noqa: WPS210
        self,
        request: requests.Request,
        cached_rate: CachedRate | None,
        junction_client: client.JunctionClient = lagom.injectable,
        offers_rates_repository: repository.OffersRatesRepository = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        query_string = request.scope["query_string"]

        offers_response = await junction_client.get_offers_by_offer_search_id(
            offers_search_id=request.path_params["offerSearchId"],
            cabin_class=query_string.get(
                "filter[groups.options.details.cabinClass]",
                [],
            ),
            include=query_string.get(
                "include",
                [],
            ),
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        if cached_rate:
            for include in offers_response.get("included", []):
                if include["type"] == "offer-options":
                    include_attributes_price_currency = include["attributes"]["price"][
                        "currency"
                    ]
                    if cached_rate.currency != include_attributes_price_currency:
                        new_money = money.from_string(
                            include["attributes"]["price"]["amount"],
                            money.Currency(include_attributes_price_currency),
                        ).convert(
                            money.Currency(cached_rate.currency),
                            decimal.Decimal(cached_rate.rate),
                        )
                        include["attributes"]["price"]["amount"] = str(new_money)
                        include["attributes"]["price"][
                            "currency"
                        ] = cached_rate.currency
        response_body = models.Body(
            data=offers_response["data"],
            links={
                "next": re.sub(
                    r"^.+\?",
                    str(
                        request.url_for(
                            "OffersByOfferSearch",
                            offerSearchId=request.path_params["offerSearchId"],
                        ),
                    )
                    + str("?"),
                    offers_response["links"]["next"],
                ),
            },
        )
        if offers_response.get("included"):
            response_body.included = offers_response.get("included")
        return models.JsonApiResponse(response_body)
