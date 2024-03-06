import dataclasses
from collections.abc import Awaitable, Callable
from typing import TypeAlias

import jwt as jwtlib
from starlette import applications, authentication, requests, responses
from starlette.middleware import base

from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.transport.http import auth

OnErrorHandler: TypeAlias = Callable[
    [requests.HTTPConnection, authentication.AuthenticationError],
    Awaitable[responses.Response],
]


class AuthenticationBackend(authentication.AuthenticationBackend):
    def __init__(
        self,
        decoder: jwt.Decoder,
        token_version: str,
    ) -> None:
        self._decoder = decoder
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
            payload = self._decoder.decode(jwt_token)
        except jwtlib.exceptions.PyJWTError as err:
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


@dataclasses.dataclass(kw_only=True, frozen=True)
class _Version1Payload(jwt.Payload):
    client_id: str


class HubHackBackend(base.BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        jwt_auth: auth.TemporaryTokenAuth,
        jwt_encoder: jwt.Encoder,
        on_error: OnErrorHandler,
    ):
        super().__init__(app)
        self._jwt = jwt_auth
        self._encoder = jwt_encoder
        self._on_error = on_error

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        if not isinstance(request.user, stdlib_auth.AuthenticatedUser):
            return await call_next(request)

        try:
            jwt_token = self._generate_jwt(request.user)
        except authentication.AuthenticationError as exc:
            return await self._on_error(request, exc)

        with self._jwt.temporary(jwt_token):
            return await call_next(request)

    def _generate_jwt(self, user: stdlib_auth.AuthenticatedUser) -> str:
        reseller_id = user.metadata.get("reseller_id")

        if not reseller_id:
            raise authentication.AuthenticationError(
                "No reseller associated with this account.",
            )

        return self._encoder.encode(_Version1Payload(client_id=reseller_id))
