import datetime
import re

import httpx
import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.service.mobile_api import repository
from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
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
        offers_repository: repository.OffersRepository = lagom.injectable,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        user_id = request.user.username
        offer_search = await junction_client.create_offer_search(
            trip_ids=body["trips"],
            passengers_dates_of_birth=[
                datetime.date.fromisoformat(passenger["dateOfBirth"])
                for passenger in body["passengers"]
            ],
        )
        await offers_repository.append_offer_search(
            user_id,
            models_pb2.OfferSearchHistoryEntity(
                offer_search_id=offer_search[_DATA_KEY][_ID_KEY],
            ),
        )
        return models.JsonApiResponse(
            models.Body(
                data=models.Resource(**offer_search[_DATA_KEY]),
            ),
            status.HTTP_201_CREATED,
        )


class OffersByOfferSearch(endpoints.HTTPEndpoint):
    async def get(  # noqa: C901,WPS231
        self,
        request: requests.Request,
        junction_client: client.JunctionClient = lagom.injectable,
        offers_rates_repository: repository.OffersRatesRepository = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        try:
            offers_response = await junction_client.get_offers_by_offer_search_id(
                offers_search_id=request.path_params["offerSearchId"],
                cabin_class=request.scope["query_string"].get(
                    "filter[groups.options.details.cabinClass]",
                    [],
                ),
                include=request.scope["query_string"].get(
                    "include",
                    [],
                ),
                cursor=pagination.cursor,
                limit=pagination.limit,
            )
        except httpx.HTTPStatusError as error:
            return models.JsonApiResponse(
                models.Body(
                    errors=error.response.json()["errors"],
                ),
                error.response.status_code,
            )
        if request.query_params.get("currency"):
            try:
                rate = get_offer_rate("EUR", request.query_params.get("currency", ""))
            except RateError as exc:
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
            if offers_response.get("included"):
                for include in offers_response.get("included", []):
                    if include["type"] == "offer-options":
                        include["attributes"]["price"]["amount"] *= rate
                        include["attributes"]["price"][
                            "currency"
                        ] = request.query_params.get("currency")
                        await offers_rates_repository.create(  # noqa: WPS220
                            identifier="_".join(
                                [
                                    include["id"],
                                    "EUR",
                                    request.query_params.get("currency", ""),
                                ],
                            ),
                            atr_value=str(rate),
                        )
        response_body = models.Body(
            data=offers_response["data"],
            links={
                "next": re.sub(
                    r"^.+\?",
                    request.url_for(
                        "OffersByOfferSearch",
                        offerSearchId=request.path_params["offerSearchId"],
                    )
                    + str("?"),
                    offers_response["links"]["next"],
                ),
            },
        )
        if offers_response.get("included"):
            response_body.included = offers_response.get("included")
        return models.JsonApiResponse(response_body)


# TODO: use currency service (!473)
def get_offer_rate(from_currency: str, to_currency: str) -> float:
    if to_currency == "SEK":
        return 11.06  # noqa: WPS432
    raise RateError("Unsupported currency")


class RateError(Exception):
    """Currency service base exception."""
