from typing import Optional

import jwt
from cryptography.hazmat.primitives import serialization
from starlette import authentication, requests


class AuthenticationBackend(authentication.AuthenticationBackend):
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
        otp = conn.scope["security"].get("otp")
        if otp:
            return self._otp_authenticate(otp)
        jwt_token = conn.scope["security"].get("jwt")
        if jwt_token:
            return self._jwt_authenticate(jwt_token)
        return None

    def _otp_authenticate(
        self,
        otp: str,
    ) -> Optional[tuple[authentication.AuthCredentials, authentication.SimpleUser]]:
        return authentication.AuthCredentials(
            ["otp_authenticated"],
        ), authentication.SimpleUser(otp)

    def _jwt_authenticate(
        self,
        jwt_token: str,
    ) -> Optional[tuple[authentication.AuthCredentials, authentication.SimpleUser]]:

        if not jwt_token:
            return None

        client_id = self._get_client_id_from_jwt_token(jwt_token)

        return authentication.AuthCredentials(
            ["jwt_authenticated"],
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
