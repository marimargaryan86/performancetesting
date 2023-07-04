from starlette import endpoints, requests, responses, status


class Alerts(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS238
        self,
        request: requests.Request,
    ) -> responses.Response:
        await request.json()

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
