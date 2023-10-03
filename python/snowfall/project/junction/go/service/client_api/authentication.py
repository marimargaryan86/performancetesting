import jwt as jwtlib
from starlette import authentication

from snowfall.stdlib.format import jwt


class LegacyAuth(object):
    def __init__(
        self,
        decoder: jwt.Decoder,
        jwt_version: str,
    ):
        self._decoder = decoder
        self._jwt_version = jwt_version

    def get_reseller_id_from_jwt(self, token: str) -> str:
        try:
            payload = self._decoder.decode(token)
        except jwtlib.PyJWTError as err:
            raise authentication.AuthenticationError("Invalid jwt token.") from err

        client_id = payload.get("client_id")

        if client_id:
            return client_id

        if payload.get("version", "0.0.0") < self._jwt_version:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        metadata = payload.get("user_info", {}).get("metadata", {})
        client_id = metadata.get("client_id")

        if not metadata.get("default_currency") and not client_id:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        return client_id
