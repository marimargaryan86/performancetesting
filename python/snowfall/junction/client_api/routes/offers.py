import datetime

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import offer_searches, offers
from snowfall.common.v1alpha import models_pb2 as common_pb2
from snowfall.junction.client_api import resources
from snowfall.junction.client_api.transformers import trip_ids_to_segments
from snowfall.junction.offers.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    models,
    pagination_helpers,
    request_helpers,
)


class Offer(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            offer = await client.get(request.path_params["offerId"])
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.OfferResource.from_proto(
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
        except trip_ids_to_segments.MissingTripsError as err:
            raise exceptions.HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ) from err

        try:
            cabin_classes = body["cabinClasses"]["data"]
        except KeyError:
            cabin_classes = []

        offer_search = await offer_search_client.create(
            request=models_pb2.OfferSearch(
                trip=models_pb2.TripOfferSearch(
                    segments=segments,
                    passengers=[
                        models_pb2.Passenger(
                            date_of_birth=protobuf.date_to_protobuf(
                                datetime.date.fromisoformat(passenger["dateOfBirth"]),
                            ),
                        )
                        for passenger in body["passengers"]
                    ],
                    cabin_classes=[
                        protobuf.slug_to_enum_value(  # type: ignore[misc]
                            descriptor=common_pb2.CabinClass.Type.DESCRIPTOR,
                            name=cabin_class,
                        )
                        for cabin_class in cabin_classes
                    ],
                ),
            ),
        )

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripOfferSearchResource.from_proto(
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
        except offer_searches.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripOfferSearchResource.from_proto(
                    offer_search=offer_search,
                    offers=[],
                    request=request,
                ),
            ),
        )


class OffersByOfferSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        search_client: offer_searches.Client = lagom.injectable,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        offer_search_id = request.path_params["offerSearchId"]

        # todo: Check should probably be done in the RPC, but that requires refactoring.
        try:
            await search_client.get(offer_search_id)
        except offer_searches.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        pagination = pagination_helpers.get_pagination(request)
        offers_page = await client.find_offers_by_offer_search(
            identifier=offer_search_id,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.OfferResource.from_proto(
                        offer=offer,
                        request=request,
                    )
                    for offer in offers_page.offers
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ViewOffersByOfferSearch",
                        offerSearchId=request.path_params["offerSearchId"],
                    ),
                    offers_page.next_page_token,
                    pagination,
                ),
            ),
        )
