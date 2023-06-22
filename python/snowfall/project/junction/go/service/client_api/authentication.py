import datetime
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

import asyncstdlib
import httpx
import jwt as jwtlib
from jwt import jwk_set_cache
from starlette import authentication, requests

from snowfall.stdlib.format import jwt


def _match_kid(signing_keys: Sequence[jwtlib.PyJWK], kid: str) -> jwtlib.PyJWK | None:
    for key in signing_keys:
        if key.key_id == kid:
            return key

    return None


class AsyncJWKClient(object):
    def __init__(
        self,
        base_url: str,
        key_ttl: datetime.timedelta,
        client: httpx.AsyncClient | None = None,
    ):
        self._client = client or httpx.AsyncClient()
        self._client.base_url = httpx.URL(base_url)
        self._jwk_set_cache = jwk_set_cache.JWKSetCache(int(key_ttl.total_seconds()))

    async def get_signing_key_from_jwt(self, token: str) -> tuple[jwtlib.PyJWK, str]:
        unverified = jwtlib.api_jwt.decode_complete(
            token,
            options={"verify_signature": False},
        )
        header = unverified["header"]

        return await self._get_signing_key(header.get("kid")), header["alg"]

    async def _get_signing_key(self, kid: str) -> jwtlib.PyJWK:
        signing_keys = await self._get_signing_keys()
        signing_key = _match_kid(signing_keys, kid)

        if not signing_key:
            # If no matching signing key from the jwk set, refresh the jwk set and try again.
            signing_keys = await self._get_signing_keys(refresh=True)
            signing_key = _match_kid(signing_keys, kid)

            if not signing_key:
                raise jwtlib.PyJWKClientError(
                    "Unable to find a signing key that matches",
                )

        return signing_key

    async def _get_signing_keys(self, *, refresh: bool = False) -> list[jwtlib.PyJWK]:
        jwk_set = await self._get_jwk_set(refresh=refresh)
        signing_keys = [
            jwk_set_key
            for jwk_set_key in jwk_set.keys
            if jwk_set_key.public_key_use in {"sig", None} and jwk_set_key.key_id
        ]

        if not signing_keys:
            raise jwtlib.PyJWKClientError(
                "The JWKS endpoint did not contain any signing keys",
            )

        return signing_keys

    async def _get_jwk_set(self, *, refresh: bool = False) -> jwtlib.PyJWKSet:
        jwk_set = None

        if not refresh:
            jwk_set = self._jwk_set_cache.get()

        if jwk_set is None:
            jwk_set = await self._fetch_data()

        if not isinstance(jwk_set, dict):
            raise jwtlib.PyJWKClientError(
                "The JWKS endpoint did not return a JSON object",
            )

        return jwtlib.PyJWKSet.from_dict(jwk_set)

    async def _fetch_data(self) -> Any:
        jwk_set: Any = None

        try:
            jwk_set = await self._fetch_keys_from_url()
        except httpx.HTTPError as err:
            raise jwtlib.exceptions.PyJWKClientConnectionError(
                "Fail to fetch data from the url",
            ) from err
        else:
            return jwk_set
        finally:
            if self._jwk_set_cache is not None:
                self._jwk_set_cache.put(jwk_set)

    async def _fetch_keys_from_url(self) -> Any:
        response = await self._client.get(url="/.well-known/jwks.json")
        response.raise_for_status()

        return response.json()


class LegacyAuth(object):
    def __init__(
        self,
        decoder: jwt.Decoder,
        jwt_version: str,
    ):
        self._decoder = decoder
        self._jwt_version = jwt_version

    def get_reseller_id_from_jwt(self, token: str) -> str:
        try:
            payload = self._decoder.decode(token)
        except jwtlib.PyJWTError as err:
            raise authentication.AuthenticationError("Invalid jwt token.") from err

        if "client_id" in payload:
            return payload["client_id"]  # noqa: WPS529

        if payload.get("version", "0.0.0") < self._jwt_version:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        metadata = payload["user_info"]["metadata"]
        client_id = metadata.get("client_id")

        if not metadata.get("default_currency") and not client_id:
            raise authentication.AuthenticationError(
                "Wrong version of jwt token. Refresh your token.",
            )

        return client_id


class OryAuth(object):
    def __init__(
        self,
        jwk_client: AsyncJWKClient,
        client: httpx.AsyncClient,
        legacy_fallback: Callable[[str], str] | None = None,
    ):
        self._jwk_client = jwk_client
        self._legacy_fallback = legacy_fallback
        self._client = client

    async def get_reseller_id_from_jwt(self, token: str) -> str:
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

        return await self._get_reseller_id_from_client_id(payload["client_id"])

    @asyncstdlib.lru_cache()
    async def _get_reseller_id_from_client_id(self, client_id: str) -> str:
        response = await self._client.get(url="/admin/clients/{0}".format(client_id))

        return response.json()["owner"]


class JWTAuthenticationBackend(authentication.AuthenticationBackend):
    def __init__(self, jwt_to_reseller_id: Callable[[str], Awaitable[str]]) -> None:
        self._jwt_to_reseller_id = jwt_to_reseller_id

    async def authenticate(
        self,
        conn: requests.HTTPConnection,
    ) -> tuple[authentication.AuthCredentials, authentication.SimpleUser] | None:
        jwt_token = conn.scope["security"].get("jwt")

        if not jwt_token:
            return None

        return authentication.AuthCredentials(
            ["authenticated"],
        ), authentication.SimpleUser(await self._jwt_to_reseller_id(jwt_token))
