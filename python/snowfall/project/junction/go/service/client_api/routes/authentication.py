import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import authentication
from snowfall.stdlib.integration.starlette import request_helpers

_DATA_KEY = "data"


class Authenticate(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        client: authentication.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            auth_token = await client.authenticate(
                body["password"],
                email=body["email"],
            )
        except (
            authentication.NotFoundError,
            authentication.InvalidArgumentError,
        ) as err:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED) from err

        payload = {
            _DATA_KEY: {
                "id": auth_token,
                "type": "user-tokens",
                "attributes": {
                    "token": auth_token,
                },
            },
        }

        return responses.JSONResponse(payload, status_code=status.HTTP_200_OK)
