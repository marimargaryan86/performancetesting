import lagom
from starlette import endpoints, requests, responses

from snowfall.junction.mobile_api import repository
from snowfall.stdlib.integration.starlette import models


class Places(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        places: repository.PlacesRepository = lagom.injectable,
    ) -> responses.Response:
        return models.JsonApiResponse(
            models.Body(
                data=await places.get(),
            ),
        )
