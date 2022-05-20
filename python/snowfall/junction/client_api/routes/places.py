import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import places
from snowfall.common.v1alpha import models_pb2
from snowfall.junction.client_api import pagination_helpers, resources
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models


class Place(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            place = await client.get(request.path_params["placeId"])
        except places.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.PlaceResource.from_proto(place, request),
            ),
        )


class Places(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find(limit=pagination.limit, cursor=pagination.cursor)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.PlaceResource.from_proto(place, request)
                    for place in response.places
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListPlaces"),
                    response.next_page_token,
                    pagination,
                ),
            ),
        )


class PlaceType(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        place_type_id = request.path_params["placeTypeId"]
        try:
            place_type = protobuf.slug_to_enum_value(
                models_pb2.Place.Type.DESCRIPTOR,
                place_type_id,
            )
        except KeyError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.PlaceTypeResource.from_proto(
                    place_type,  # type: ignore
                    request,
                ),
            ),
        )


class PlaceTypes(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)

        sequence_page = pagination_helpers.sequence_paginator(
            sequence=models_pb2.Place.Type.values(),
            pagination=pagination,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.PlaceTypeResource.from_proto(
                        place_type,
                        request,
                    )
                    for place_type in sequence_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListPlaceTypes"),
                    sequence_page.next_page_token,
                    pagination,
                ),
            ),
        )
