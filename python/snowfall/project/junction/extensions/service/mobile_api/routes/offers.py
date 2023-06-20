import datetime
import re

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.stdlib.integration.starlette import (
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.vendor.junction.go import client

_DATA_KEY = "data"
_ID_KEY = "id"
_ATTRIBUTES_KEY = "attributes"
_TYPE_KEY = "type"
_DETAILS_KEY = "details"


class OfferSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_client: client.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
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
        junction_client: client.Client = lagom.injectable,
    ) -> responses.Response:
        offer_search = await junction_client.get_offer_search(
            offers_search_id=request.path_params["offerSearchId"],
            include=request.scope["parsed_query_string"].get(
                "include",
                [],
            ),
        )
        response_body = models.Body(data=offer_search["data"])
        if offer_search.get("included"):
            response_body.included = offer_search.get("included")
        return models.JsonApiResponse(response_body)


class OffersByOfferSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        junction_client: client.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        query_string = request.scope["parsed_query_string"]

        offers_response = await junction_client.get_offers_by_offer_search_id(
            offers_search_id=request.path_params["offerSearchId"],
            cabin_class=query_string.get(
                "filter[groups.options.details.cabinClass][eq]",
                [],
            ),
            include=query_string.get(
                "include",
                [],
            ),
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

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
                    + "?",
                    offers_response["links"]["next"],
                ),
            },
        )
        if offers_response.get("included"):
            response_body.included = offers_response.get("included")
        return models.JsonApiResponse(response_body)
