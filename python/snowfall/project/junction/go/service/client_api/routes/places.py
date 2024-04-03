import dataclasses

from starlette import responses

from snowfall.project.junction.go.adapter import places
from snowfall.project.junction.go.service.client_api import resources
from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers


@dataclasses.dataclass(frozen=True)
class Places:
    _client: places.Client

    async def view(self, request: messages.Request) -> responses.Response:
        place = await self._client.get(request.path_params["placeId"])

        return models.JsonApiResponse(
            models.Body(
                data=resources.PlaceResource.from_proto(
                    place,
                    request.starlette_request,
                ),
            ),
        )

    async def list_(self, request: messages.Request) -> responses.Response:
        response = await self._client.find(
            limit=request.pagination.limit,
            cursor=request.pagination.cursor,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.PlaceResource.from_proto(place, request.starlette_request)
                    for place in response.places
                ],
                links=pagination_helpers.get_next_url(
                    request.starlette_request.url_for("ListPlaces"),
                    response.next_page_token,
                    request.pagination,
                ),
            ),
        )
