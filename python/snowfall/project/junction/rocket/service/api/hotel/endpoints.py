from starlette import endpoints, requests, responses, status


class HotelSearch(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
    ) -> responses.Response:
        return responses.Response(status_code=status.HTTP_200_OK, content={})


class HotelSearchStatus(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        return responses.Response(status_code=status.HTTP_200_OK, content={})


class HotelSearchRetrieval(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        return responses.Response(
            status_code=status.HTTP_200_OK,
            content={},
        )
