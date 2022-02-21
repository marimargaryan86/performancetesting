import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall import fixtures
from snowfall.adapter import offer_searches
from snowfall.junction.client_api import models, request_helpers, resources
from snowfall.junction.offers.v1alpha import offers_pb2


class OfferSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        client: offer_searches.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        if fixtures.NOT_FOUND in body["trips"]:
            raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

        offer_search = await client.create(
            request=offers_pb2.SearchTripOffersRequest(
                search=offers_pb2.TripOfferSearch(
                    passengers=[
                        offers_pb2.Passenger(age=passenger["age"])
                        for passenger in body["passengers"]
                    ],
                ),
            ),
        )

        return models.JsonApiResponse(
            models.Body(
                data=await resources.TripOfferSearchResource.from_proto(
                    offer_search=offer_search,
                    offers=[],
                    request=request,
                ),
            ),
            status.HTTP_201_CREATED,
        )
