from typing import Any, AsyncGenerator

import httpx

from snowfall.vendor.junction import client

_BASE_URL = "https://snowfalltravel.com/foo"
_AUTH_HEADER = "Authorization"
_AUTH_TOKEN = "Bearer foo"  # nosec


class _TestClient(client.BaseClient):
    async def test_endpoint(self) -> dict[str, Any]:
        response = await self.client.get("/bar")
        response.raise_for_status()

        return response.json()

    async def unnecessary_format_endpoint(self) -> dict[str, Any]:
        response = await self.client.get("{0}/bar".format(self._base_url))
        response.raise_for_status()

        return response.json()


class _TestAuth(httpx.Auth):
    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers.update(httpx.Headers({_AUTH_HEADER: _AUTH_TOKEN}))

        yield request


def _verify_request_base_path(request: httpx.Request) -> httpx.Response:
    assert str(request.url) == "{0}/bar".format(_BASE_URL)

    return httpx.Response(200, json={})


def _verify_request_bearer_token(request: httpx.Request) -> httpx.Response:
    assert request.headers.get(_AUTH_HEADER) == _AUTH_TOKEN

    return httpx.Response(200, json={})


async def test_base_url_works() -> None:
    transport = httpx.MockTransport(_verify_request_base_path)
    pay = _TestClient(
        base_url=_BASE_URL,
        client=httpx.AsyncClient(transport=transport),
    )
    await pay.test_endpoint()


async def test_base_url_works_with_unnecessary_format() -> None:
    transport = httpx.MockTransport(_verify_request_base_path)
    pay = _TestClient(
        base_url=_BASE_URL,
        client=httpx.AsyncClient(transport=transport),
    )
    await pay.unnecessary_format_endpoint()


async def test_auth_is_applied() -> None:
    transport = httpx.MockTransport(_verify_request_bearer_token)
    pay = _TestClient(
        base_url=_BASE_URL,
        auth=_TestAuth(),
        client=httpx.AsyncClient(transport=transport),
    )
    await pay.test_endpoint()
