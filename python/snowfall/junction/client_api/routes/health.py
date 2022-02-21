from starlette import endpoints, requests, responses

from snowfall.junction.client_api import models


class Health(endpoints.HTTPEndpoint):
    async def get(self, request: requests.Request) -> responses.Response:
        return models.JsonApiResponse(models.Body(meta={"status": "pass"}))
