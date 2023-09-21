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
    ) -> tuple[authentication.AuthCredentials, authentication.SimpleUser] | None:
        otp = conn.scope["security"].get("otp")

        if otp is not None:
            return self._otp_authenticate(otp)

        jwt_token = conn.scope["security"].get("jwt")

        if jwt_token is not None:
            return self._jwt_authenticate(jwt_token)

        return None

    def _otp_authenticate(
        self,
        otp: str | None,
    ) -> tuple[authentication.AuthCredentials, authentication.SimpleUser]:
        if not otp:
            raise authentication.AuthenticationError("Empty OTP found.")

        return authentication.AuthCredentials(
            ["otp_authenticated"],
        ), authentication.SimpleUser(otp)

    def _jwt_authenticate(
        self,
        jwt_token: str | None,
    ) -> tuple[authentication.AuthCredentials, authentication.SimpleUser]:
        if not jwt_token:
            raise authentication.AuthenticationError("Invalid JWT token.")

        client_id = self._get_client_id_from_jwt_token(jwt_token)

        return authentication.AuthCredentials(
            ["jwt_authenticated"],
        ), authentication.SimpleUser(client_id)

    def _get_client_id_from_jwt_token(self, jwt_token: str) -> str:
        try:
            payload = self._get_payload_from_jwt_token(jwt_token)
        except jwt.exceptions.PyJWTError as err:
            raise authentication.AuthenticationError("Invalid JWT token.") from err

        if payload.get("version") != self._token_version:
            raise authentication.AuthenticationError(
                "Wrong version of JWT token. Refresh your token.",
            )

        if "client_id" not in payload:
            raise authentication.AuthenticationError(
                "Wrong version of JWT token. Refresh your token.",
            )

        return payload["client_id"]

    def _get_payload_from_jwt_token(self, jwt_token: str) -> dict[str, str]:
        key = serialization.load_pem_public_key(self._public_key.encode())

        return jwt.decode(
            jwt=jwt_token,
            key=key,  # type: ignore[arg-type]
            algorithms=["RS256"],
        )
