import datetime

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import offer_searches, offers
from snowfall.junction.client_api import models, request_helpers, resources
from snowfall.junction.client_api.transformers import trip_ids_to_segments
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.stdlib.format import protobuf


class Offer(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            offer = await client.get(request.path_params["offerId"])
        except offers.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=await resources.OfferResource.from_proto(
                    offer=offer,
                    request=request,
                ),
            ),
        )


class OfferSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        trips_to_segments: trip_ids_to_segments.TripIdsToSegments = lagom.injectable,
        offer_search_client: offer_searches.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            segments = await trips_to_segments.transform(trip_ids=body["trips"])
        except trip_ids_to_segments.MissingTripsError:
            raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

        offer_search = await offer_search_client.create(
            request=offers_pb2.OfferSearch(
                trip=offers_pb2.TripOfferSearch(
                    segments=segments,
                    passengers=[
                        offers_pb2.Passenger(
                            date_of_birth=protobuf.date_to_protobuf(
                                datetime.date.fromisoformat(passenger["dateOfBirth"]),
                            ),
                        )
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


class OfferSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offer_searches.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            offer_search = await client.get(request.path_params["offerSearchId"])
        except offer_searches.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=await resources.TripOfferSearchResource.from_proto(
                    offer_search=offer_search,
                    offers=[],
                    request=request,
                ),
            ),
        )
