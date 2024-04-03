from starlette import endpoints, requests, responses


class Quotes(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
    ) -> responses.Response:
        return responses.Response()
