import lagom
from furl import furl
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import places
from snowfall.junction.client_api import models, request_helpers, resources


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
        cursor = request.query_params[request_helpers.PAGE_CURSOR_KEY]
        limit = int(request.query_params[request_helpers.PAGE_LIMIT_KEY])
        response = await client.find(limit=limit, cursor=cursor)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.PlaceResource.from_proto(place, request)
                    for place in response.places
                ],
                links={
                    "next": request_helpers.get_next_url(
                        furl(request.url_for("ListPlaces")),
                        response.next_page_token,
                        limit,
                    ),
                },
            ),
        )
