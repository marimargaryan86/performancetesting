from typing import Optional

import jwt
from cryptography.hazmat.primitives import serialization
from starlette import authentication, requests


class JWTAuthenticationBackend(authentication.AuthenticationBackend):
    def __init__(
        self,
        public_key: str,
        token_version: str,
    ) -> None:
        self._public_key = public_key
        self._token_version = token_version

    async def authenticate(
        self,
        conn: requests.HTTPConnection,
    ) -> Optional[tuple[authentication.AuthCredentials, authentication.SimpleUser]]:
        jwt_token = conn.scope.get("jwt")

        if not jwt_token:
            return None

        client_id = self._get_client_id_from_jwt_token(jwt_token)

        return authentication.AuthCredentials(
            ["authenticated"],
        ), authentication.SimpleUser(client_id)

    def _get_client_id_from_jwt_token(self, jwt_token: str) -> str:
        try:
            payload = self._get_payload_from_jwt_token(jwt_token)
        except jwt.exceptions.PyJWTError as err:
            raise authentication.AuthenticationError("Invalid jwt token.") from err

        if payload.get("version") != self._token_version:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        if "client_id" not in payload:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        return payload["client_id"]

    def _get_payload_from_jwt_token(self, jwt_token: str) -> dict[str, str]:
        key = serialization.load_pem_public_key(self._public_key.encode())

        return jwt.decode(
            jwt=jwt_token,
            key=key,  # type: ignore[arg-type]
            algorithms=["RS256"],
        )
