import contextlib
import contextvars
import dataclasses
from collections.abc import AsyncGenerator, Iterator
from typing import TypedDict

import httpx


class J1Credentials(TypedDict):
    org_id: str
    j1_authorization: str


ResellerCredentialsMapping = dict[str, J1Credentials]

_reseller_id: contextvars.ContextVar[str] = contextvars.ContextVar("reseller_id")


@dataclasses.dataclass(frozen=True)
class JunctionOneAuth:
    authorization: str
    api_key: str


class TokenAuth(httpx.Auth):
    def __init__(self, auth: JunctionOneAuth):
        self._auth = auth

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers.update({
            "X-Api-Key": self._auth.api_key,
            "Authorization": self._auth.authorization,
        })
        yield request


class TemporaryTokenAuth(httpx.Auth):
    def __init__(
        self,
        *,
        api_key: str,
        reseller_credentials_mapping: ResellerCredentialsMapping,
    ):
        self._api_key = api_key
        self._reseller_credentials_mapping = reseller_credentials_mapping

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers.update({
            "X-Api-Key": self._api_key,
            "Authorization": self._get_creds()["j1_authorization"],
        })

        yield request

    @contextlib.contextmanager
    def temporary(self, reseller_id: str) -> Iterator[None]:
        context_token = _reseller_id.set(reseller_id)

        try:
            yield
        finally:
            _reseller_id.reset(context_token)

    def get_org_id(self) -> int:
        return int(self._get_creds()["org_id"])

    def _get_creds(self) -> J1Credentials:
        try:
            reseller_id = _reseller_id.get()
        except LookupError as err:
            raise ValueError("reseller_id not set") from err

        creds = self._reseller_credentials_mapping.get(reseller_id)

        if not creds:
            raise ValueError("No credentials for reseller_id.")

        return creds
