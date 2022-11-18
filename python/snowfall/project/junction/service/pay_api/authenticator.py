from typing import Mapping, Optional, Tuple

from starlette import authentication, requests

from snowfall.stdlib import jwt


class Authenticator(jwt.JWTDecoder):
    def __init__(self, public_key_content: str):
        super().__init__(public_key_content, "RS256")

    async def authenticate(
        self,
        conn: requests.HTTPConnection,
    ) -> Optional[Tuple[authentication.AuthCredentials, authentication.BaseUser]]:
        jwt_token = conn.scope["security"].get("jwt")

        if not jwt_token:
            return (
                authentication.AuthCredentials(),
                authentication.UnauthenticatedUser(),
            )

        try:
            decoded = self.decode_token(jwt_token)
        except jwt.jwt.exceptions.ExpiredSignatureError as err:
            raise authentication.AuthenticationError(str(err)) from err

        client_id: str = decoded["user_info"]["id"]

        return authentication.AuthCredentials(
            ["authenticated"],
        ), authentication.SimpleUser(client_id)

    def decode_token(self, jwt_token: str) -> Mapping[str, Mapping[str, str]]:
        return self.decode(jwt_token)
