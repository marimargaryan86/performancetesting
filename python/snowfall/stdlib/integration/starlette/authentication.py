from collections.abc import Awaitable, Callable

import jwt as jwtlib
from starlette import authentication, requests

from snowfall.stdlib.format import jwt


class OryAuth(object):
    def __init__(
        self,
        jwk_client: jwt.AsyncJWKClient,
        client_resolver: Callable[[str], Awaitable[str]],
        legacy_fallback: Callable[[str], str] | None = None,
    ):
        self._jwk_client = jwk_client
        self._client_resolver = client_resolver
        self._legacy_fallback = legacy_fallback

    async def get_owner_from_jwt(self, token: str) -> str:
        try:
            signing_key, alg = await self._jwk_client.get_signing_key_from_jwt(token)
        except jwtlib.PyJWTError as ory_err:
            if self._legacy_fallback:
                return self._legacy_fallback(token)

            raise authentication.AuthenticationError("Invalid jwt token.") from ory_err

        try:
            payload = jwtlib.decode(
                token,
                signing_key.key,
                algorithms=[alg],
            )
        except jwtlib.PyJWTError as err:
            raise authentication.AuthenticationError("Invalid jwt token.") from err

        return await self._client_resolver(payload["client_id"])


class JWTAuthenticationBackend(authentication.AuthenticationBackend):
    def __init__(self, jwt_to_user_id: Callable[[str], Awaitable[str]]):
        self._jwt_to_user_id = jwt_to_user_id

    async def authenticate(
        self,
        conn: requests.HTTPConnection,
    ) -> tuple[authentication.AuthCredentials, authentication.SimpleUser] | None:
        jwt_token = conn.scope["security"].get("jwt")

        if not jwt_token:
            return None

        return authentication.AuthCredentials(
            ["authenticated"],
        ), authentication.SimpleUser(await self._jwt_to_user_id(jwt_token))
