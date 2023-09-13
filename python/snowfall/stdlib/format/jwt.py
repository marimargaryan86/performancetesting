import base64
import dataclasses
import datetime
from collections.abc import Mapping, Sequence
from typing import Any

import httpx
import jwt
from jwt.jwk_set_cache import JWKSetCache

from snowfall.stdlib import types


def _match_kid(signing_keys: Sequence[jwt.PyJWK], kid: str) -> jwt.PyJWK | None:
    for key in signing_keys:
        if key.key_id == kid:
            return key

    return None


class AsyncJWKClient(object):
    def __init__(
        self,
        jwk_url: str,
        key_ttl: datetime.timedelta,
        client: httpx.AsyncClient | None = None,
    ):
        self._client = client or httpx.AsyncClient()
        self._jwk_url = jwk_url
        self._jwk_set_cache = JWKSetCache(int(key_ttl.total_seconds()))

    async def get_signing_key_from_jwt(self, token: str) -> tuple[jwt.PyJWK, str]:
        unverified = jwt.api_jwt.decode_complete(
            token,
            options={"verify_signature": False},
        )
        header = unverified["header"]
        kid = header.get("kid")

        if not kid:
            raise jwt.PyJWKError("JWT is missing 'kid' header")

        return await self._get_signing_key(kid), header["alg"]

    async def _get_signing_key(self, kid: str) -> jwt.PyJWK:
        signing_keys = await self._get_signing_keys()
        signing_key = _match_kid(signing_keys, kid)

        if not signing_key:
            # If no matching signing key from the jwk set, refresh the jwk set and try again.
            signing_keys = await self._get_signing_keys(refresh=True)
            signing_key = _match_kid(signing_keys, kid)

            if not signing_key:
                raise jwt.PyJWKClientError(
                    "Unable to find a signing key that matches",
                )

        return signing_key

    async def _get_signing_keys(self, *, refresh: bool = False) -> list[jwt.PyJWK]:
        jwk_set = await self._get_jwk_set(refresh=refresh)
        signing_keys = [
            jwk_set_key
            for jwk_set_key in jwk_set.keys
            if jwk_set_key.public_key_use in {"sig", None} and jwk_set_key.key_id
        ]

        if not signing_keys:
            raise jwt.PyJWKClientError(
                "The JWKS endpoint did not contain any signing keys",
            )

        return signing_keys

    async def _get_jwk_set(self, *, refresh: bool = False) -> jwt.PyJWKSet:
        jwk_set = None

        if not refresh:
            jwk_set = self._jwk_set_cache.get()

        if jwk_set is None:
            jwk_set = await self._fetch_data()

        if not isinstance(jwk_set, dict):
            raise jwt.PyJWKClientError(
                "The JWKS endpoint did not return a JSON object",
            )

        return jwt.PyJWKSet.from_dict(jwk_set)

    async def _fetch_data(self) -> Any:
        jwk_set: Any = None

        try:
            jwk_set = await self._fetch_keys_from_url()
        except httpx.HTTPError as err:
            raise jwt.exceptions.PyJWKClientConnectionError(
                "Fail to fetch data from the url",
            ) from err
        else:
            return jwk_set
        finally:
            if self._jwk_set_cache is not None:
                self._jwk_set_cache.put(jwk_set)

    async def _fetch_keys_from_url(self) -> Any:
        response = await self._client.get(url=self._jwk_url)
        response.raise_for_status()

        return response.json()


@dataclasses.dataclass(frozen=True)
class Payload(object):
    custom: Mapping[str, types.Primitive] = dataclasses.field(default_factory=dict)
    iss: str | None = None
    sub: str | None = None
    aud: str | None = None
    exp: int | datetime.datetime | None = None
    nbf: int | datetime.datetime | None = None
    iat: int | datetime.datetime | None = None
    jti: str | None = None


class Encoder(object):
    def __init__(
        self,
        private_key: str | None = None,
        algorithm: str = "HS256",
    ):
        self._algorithm = algorithm
        self._key = ""

        if private_key:
            self._key = _decode_base64_key(private_key)

        # Verify that the chosen algorithm works with the provided key.
        jwt.encode({}, self._key, algorithm=self._algorithm)

    def encode(self, payload: Payload, headers: Mapping[str, Any] | None = None) -> str:
        return jwt.encode(
            payload={
                jwt_key: jwt_value
                for jwt_key, jwt_value in dataclasses.asdict(payload).items()
                if jwt_value is not None
            },
            key=self._key,
            headers=dict(headers) if headers else None,
            algorithm=self._algorithm,
        )


class Decoder(object):
    def __init__(
        self,
        public_key: str | None = None,
        algorithms: Sequence[str] | None = None,
    ):
        self._algorithms = ["HS256"]
        self._key = ""

        if public_key:
            self._key = _decode_base64_key(public_key)

        if algorithms:
            self._algorithms = list(algorithms)

    def decode(
        self,
        jwt_token: str,
    ) -> Mapping[str, Any]:
        return jwt.decode(
            jwt_token,
            self._key,
            algorithms=self._algorithms,
        )


def _decode_base64_key(encoded_key: str) -> str:
    return base64.b64decode(encoded_key.encode()).decode()
