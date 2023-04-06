from starlette import authentication, requests

from snowfall.stdlib.format import jwt


class Authenticator(jwt.Decoder):
    def __init__(self, public_key_content: str):
        super().__init__(public_key_content, ["RS256"])

    async def authenticate(
        self,
        conn: requests.HTTPConnection,
    ) -> tuple[authentication.AuthCredentials, authentication.BaseUser] | None:
        jwt_token = conn.scope["security"].get("jwt")

        if not jwt_token:
            return (
                authentication.AuthCredentials(),
                authentication.UnauthenticatedUser(),
            )

        try:
            decoded = self.decode(jwt_token)
        except jwt.jwt.exceptions.ExpiredSignatureError as err:
            raise authentication.AuthenticationError(str(err)) from err
        except jwt.jwt.exceptions.DecodeError as err:
            # TODO: does not handle the exception proeprly (like not showing the err msg)
            raise authentication.AuthenticationError("Invalid JWT token") from err

        client_id: str = decoded["user_info"]["id"]

        return authentication.AuthCredentials(
            ["authenticated"],
        ), authentication.SimpleUser(client_id)
