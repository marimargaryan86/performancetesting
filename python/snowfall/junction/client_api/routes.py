from starlette import endpoints, requests, responses

from snowfall.junction.client_api import handlers


class Health(endpoints.HTTPEndpoint):
    async def get(self, request: requests.Request) -> responses.Response:
        return handlers.JsonApiResponse({"meta": {"status": "ok"}})
