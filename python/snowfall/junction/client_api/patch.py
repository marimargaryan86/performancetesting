from base64 import b64decode
from typing import Any

import jwt
import pydantic
from cryptography.hazmat.primitives import serialization
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)
from starlette.requests import HTTPConnection


class AuthSettings(pydantic.BaseSettings):
    jwt_public_key: str
    jwt_token_version: str

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.jwt_public_key = b64decode(self.jwt_public_key.encode()).decode()


class JWTAuthenticationBackend(AuthenticationBackend):
    def __init__(self, settings: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.settings = settings

    async def authenticate(
        self,
        conn: HTTPConnection,
    ) -> tuple[AuthCredentials, SimpleUser]:
        if "Authorization" not in conn.headers:
            raise AuthenticationError("Authorization header not found.")

        jwt_token = self._get_jwt_token_from_authorization_header(
            conn.headers["Authorization"],
        )
        client_id = self._get_client_id_from_jwt_token(jwt_token)

        return AuthCredentials(["authenticated"]), SimpleUser(client_id)

    def _get_jwt_token_from_authorization_header(self, auth_header: str) -> str:
        try:
            auth_type, jwt_token = auth_header.split(" ", 1)
        except ValueError:
            raise AuthenticationError(
                "Could not parse the Authorization header:"
                + " '{0}'.".format(auth_header)
                + " The Authorization header should be in the form of"
                + " 'Bearer jwt-token'.",
            )

        if auth_type.lower() != "bearer":
            raise AuthenticationError(
                "Could not parse the Authorization header:"
                + " '{0}'.".format(auth_header)
                + " The Authorization header should be in the form of"
                + " 'Bearer jwt-token'.",
            )

        return jwt_token

    def _get_client_id_from_jwt_token(self, jwt_token: str) -> str:
        try:
            payload = self._get_payload_from_jwt_token(jwt_token)
        except jwt.exceptions.PyJWTError:
            raise AuthenticationError("Invalid jwt token.")

        if payload.get("version") != self.settings.jwt_token_version:
            raise AuthenticationError("Wrong version of jwt token. Refresh your token.")

        if "client_id" not in payload:
            raise AuthenticationError("Wrong version of jwt token. Refresh your token.")

        return payload["client_id"]

    def _get_payload_from_jwt_token(self, jwt_token: str) -> dict[str, str]:
        key = serialization.load_pem_public_key(self.settings.jwt_public_key.encode())

        return jwt.decode(
            jwt=jwt_token,
            key=key,  # type: ignore[arg-type]
            algorithms=["RS256"],
        )
