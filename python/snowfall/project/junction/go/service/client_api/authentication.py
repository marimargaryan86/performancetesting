import jwt as jwtlib
from starlette import authentication, requests

from snowfall.stdlib.format import jwt


class JWTAuthenticationBackend(authentication.AuthenticationBackend):
    def __init__(
        self,
        decoder: jwt.Decoder,
        jwt_version: str,
    ) -> None:
        self._decoder = decoder
        self._jwt_version = jwt_version

    async def authenticate(
        self,
        conn: requests.HTTPConnection,
    ) -> tuple[authentication.AuthCredentials, authentication.SimpleUser] | None:
        jwt_token = conn.scope["security"].get("jwt")

        if not jwt_token:
            return None

        client_id = self._get_client_id_from_jwt_token(jwt_token)

        return authentication.AuthCredentials(
            ["authenticated"],
        ), authentication.SimpleUser(client_id)

    def _get_client_id_from_jwt_token(self, jwt_token: str) -> str:
        try:
            payload = self._decoder.decode(jwt_token)
        except jwtlib.exceptions.PyJWTError as err:
            raise authentication.AuthenticationError("Invalid jwt token.") from err

        if "client_id" in payload:
            return payload["client_id"]  # noqa: WPS529

        if payload.get("version", "0.0.0") < self._jwt_version:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        metadata = payload["user_info"]["metadata"]
        client_id = metadata.get("client_id")

        if not metadata.get("default_currency") and not client_id:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        return client_id
