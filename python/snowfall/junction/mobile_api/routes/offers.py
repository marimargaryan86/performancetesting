import datetime

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.junction.client_api import resources
from snowfall.junction.mobile_api import repository
from snowfall.stdlib.integration.starlette import models, request_helpers
from snowfall.vendor.junction import client


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
            offer_search["data"]["id"],
        )
        return models.JsonApiResponse(
            models.Body(data=resources.TripOfferSearchResource(**offer_search["data"])),
            status.HTTP_201_CREATED,
        )


class OffersByOfferSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        offer_search_id = request.path_params["offerSearchId"]
        offers = await junction_client.get_offers_by_offer_search_id(offer_search_id)

        ret = [resources.TripOfferSearchResource(**offer) for offer in offers["data"]]

        return models.JsonApiResponse(
            models.Body(data=ret, links=offers["links"]),
        )
