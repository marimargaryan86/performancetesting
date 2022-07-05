import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.service.mobile_api import repository, resources
from snowfall.stdlib.integration.starlette import models

_SEARCH_KEY = "query[name]"


class Places(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        places_repository: repository.PlacesRepository = lagom.injectable,
    ) -> responses.Response:
        search_key = request.query_params.get(_SEARCH_KEY)
        if search_key is None:
            places = await places_repository.find()
        else:
            places = await places_repository.match(search_key)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.PlaceResource.from_proto(place) async for place in places
                ],
            ),
        )
