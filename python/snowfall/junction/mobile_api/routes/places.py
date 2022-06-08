import lagom
from starlette import endpoints, requests, responses

from snowfall.junction.mobile_api import repository
from snowfall.stdlib.integration.starlette import models

_SEARCH_KEY = "query[name]"


class Places(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        places_repository: repository.PlacesRepository = lagom.injectable,
    ) -> responses.Response:
        search_key = request.query_params.get(_SEARCH_KEY)
        if not search_key:
            return models.JsonApiResponse(
                models.Body(
                    data=await places_repository.find(),
                ),
            )
        return models.JsonApiResponse(
            models.Body(
                data=await places_repository.match(search_key),
            ),
        )
