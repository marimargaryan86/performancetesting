import datetime
import re

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
    async def get(
        self,
        request: requests.Request,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
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
