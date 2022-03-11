import lagom
from furl import furl
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import places
from snowfall.junction.client_api import models, resources


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
                data=await resources.PlaceResource.from_proto(place, request),
            ),
        )


class Places(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        cursor = request.query_params["page[cursor]"]
        limit = int(request.query_params["page[limit]"])
        response = await client.find(limit=limit, cursor=cursor)
        resource_list = [
            await resources.PlaceResource.from_proto(place, request)
            for place in response.places
        ]

        next_url = furl(request.url_for("ListPlaces"))
        next_url.args["page[cursor]"] = response.next_page_token
        next_url.args["page[limit]"] = limit

        return models.JsonApiResponse(
            models.Body(
                data=resource_list,
                links={
                    "next": next_url.url,
                },
            ),
        )
