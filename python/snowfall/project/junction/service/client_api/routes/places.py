import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.adapter import places
from snowfall.project.junction.service.client_api import resources
from snowfall.project.junction.service.places.v1alpha import models_pb2
from snowfall.stdlib import sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models, pagination_helpers


class Place(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        place = await client.get(request.path_params["placeId"])

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
                models_pb2.Location.Type.DESCRIPTOR,
                place_type_id,
            )
        except KeyError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.PlaceTypeResource.from_proto(
                    place_type,  # type: ignore[arg-type]
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
        sequence_page = sequence.paginate(
            sequence=models_pb2.Location.Type.values(),
            cursor=pagination.cursor,
            limit=pagination.limit,
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
                    sequence_page.cursor,
                    pagination,
                ),
            ),
        )
