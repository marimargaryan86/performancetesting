import dataclasses
import inspect
from typing import Dict, Optional

import httpx

from snowfall.vendor.direct_ferries import errors
from snowfall.vendor.direct_ferries.clients import auth


@dataclasses.dataclass(frozen=True)
class RequestDetails(object):
    url: str
    method: str
    payload: Optional[str] = None
    query_params: Optional[httpx.QueryParams] = None


@dataclasses.dataclass(frozen=True)
class ClientConfig(object):
    client_id: str
    client_secret: str
    api_url: str
    partner_code: str
    timeout: int = 120
    api_version: Optional[str] = "v1.0"


class BaseClient(object):
    """Direct Ferries API client library."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        auth_client: auth.AuthClient,
        config: ClientConfig,
    ) -> None:
        self._http_client = http_client
        self._auth_client = auth_client
        self._config = config
        self._auth_response: Optional[auth.AuthServiceResponse] = None

    async def _make_request(
        self,
        request_details: RequestDetails,
    ) -> httpx.Response:
        try:
            response = await self._http_client.request(
                method=request_details.method,
                url=request_details.url,
                content=request_details.payload,
                params=request_details.query_params,
                headers=await self._default_headers(),
            )
        except httpx.HTTPError as raw_exc:
            raise errors.DFServiceError(inspect.getdoc(raw_exc)) from raw_exc

        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.DFServiceError(
                errors.get_response_error_message(response),
            ) from exc

        return response

    async def _auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": "Bearer {0}".format(await self._auth_client.get_token()),
        }

    async def _default_headers(self) -> Dict[str, str]:
        return {
            "content-type": "application/json",
            **await self._auth_headers(),
        }

    @property
    def _request_params(self) -> Dict[str, str]:
        return {"culture": "en-GB"}
