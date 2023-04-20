import dataclasses
from typing import cast

from starlette import exceptions, responses, status

from snowfall.adapter import authentication
from snowfall.stdlib.integration.starlette import messages

_DATA_KEY = "data"


@dataclasses.dataclass(frozen=True)
class Authenticate(object):
    _client: authentication.Client

    async def create(self, request: messages.Request) -> responses.Response:
        try:
            auth_token = await self._client.authenticate(
                cast(str, request.body["password"]),
                email=cast(str, request.body["email"]),
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
