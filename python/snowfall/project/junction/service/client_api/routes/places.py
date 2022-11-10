import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.adapter import places
from snowfall.project.junction.service.client_api import resources
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
