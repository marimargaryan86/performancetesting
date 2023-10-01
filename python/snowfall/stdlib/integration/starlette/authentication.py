import dataclasses
from collections.abc import Awaitable, Callable
from typing import Any, Literal

import jwt as jwtlib
from starlette import authentication, requests

from snowfall.stdlib import authentication as stdlib_auth
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

            raise authentication.AuthenticationError("Invalid JWT token.") from ory_err

        try:
            payload = jwtlib.decode(
                token,
                signing_key.key,
                algorithms=[alg],
            )
        except jwtlib.PyJWTError as err:
            raise authentication.AuthenticationError("Invalid JWT token.") from err

        return await self._client_resolver(payload["client_id"])


class JWTAuthenticationBackend(authentication.AuthenticationBackend):
    def __init__(self, jwt_to_user_id: Callable[[str], Awaitable[str]]):
        self._jwt_to_user_id = jwt_to_user_id

    async def authenticate(
        self,
        conn: requests.HTTPConnection,
    ) -> tuple[authentication.AuthCredentials, authentication.SimpleUser] | None:
        jwt_token = conn.scope["security"].get("jwt")

        if jwt_token is None:
            return None

        if not jwt_token:
            raise authentication.AuthenticationError("Invalid JWT token.")

        return authentication.AuthCredentials(
            ["authenticated"],
        ), authentication.SimpleUser(await self._jwt_to_user_id(jwt_token))


@dataclasses.dataclass(frozen=True)
class AuthenticatedUser(authentication.BaseUser):
    identifier: str
    email: str
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    @property
    def is_authenticated(self) -> Literal[True]:
        return True

    @property
    def display_name(self) -> str:
        return self.email

    @property
    def username(self) -> str:
        return self.email

    @property
    def identity(self) -> str:
        return self.identifier


class CookieAuthenticationBackend(authentication.AuthenticationBackend):
    def __init__(self, cookie_to_user: Callable[[str], Awaitable[stdlib_auth.User]]):
        self._cookie_to_user = cookie_to_user

    async def authenticate(
        self,
        conn: requests.HTTPConnection,
    ) -> tuple[authentication.AuthCredentials, AuthenticatedUser] | None:
        cookie_value = conn.scope["security"].get("cookie")

        if cookie_value is None:
            return None

        if not cookie_value:
            raise authentication.AuthenticationError("Empty cookie found.")

        try:
            ory_user = await self._cookie_to_user(cookie_value)
        except stdlib_auth.AuthenticationError as err:
            raise authentication.AuthenticationError("Session not found.") from err

        return authentication.AuthCredentials(
            ["authenticated"],
        ), AuthenticatedUser(
            identifier=ory_user.identifier,
            email=ory_user.email,
            metadata=ory_user.metadata,
        )
