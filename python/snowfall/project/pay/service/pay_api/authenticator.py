import jwt as jwtlib
from starlette import authentication

from snowfall.stdlib.format import jwt


class LegacyAuth(object):
    def __init__(
        self,
        decoder: jwt.Decoder,
    ):
        self._decoder = decoder

    def get_user_id_from_jwt(self, token: str) -> str:
        try:
            payload = self._decoder.decode(token)
        except jwtlib.PyJWTError as err:
            raise authentication.AuthenticationError("Invalid jwt token.") from err

        user_info = payload.get("user_info")

        if not user_info:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        user_id = user_info.get("id")

        if not user_info:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        return user_id
