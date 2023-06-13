import time
from collections.abc import Callable
from typing import Any
from unittest import mock

import freezegun
import httpx
import jwt

from snowfall.vendor.junction import auth

_BASE_URL = "https://snowfalltravel.com/foo"


def _token_response(time_offset: int) -> dict[str, Any]:
    token = jwt.encode({"exp": time.time() + time_offset}, "foo")

    return {
        "data": {
            "id": token,
            "type": "user-tokens",
            "attributes": {
                "token": token,
            },
        },
    }


def _valid_token(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_token_response(1))


def _expired_token(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_token_response(-1))


def _create_authorization(
    request_handler: Callable[[httpx.Request], httpx.Response],
) -> auth.UserAuth:
    transport = httpx.MockTransport(request_handler)

    return auth.UserAuth(
        base_url=_BASE_URL,
        client=httpx.AsyncClient(transport=transport),
        email="foo",
        password="bar",  # nosec
    )


@freezegun.freeze_time()
async def test_auth_header_updates() -> None:
    authorization = _create_authorization(_valid_token)
    request = httpx.Request("GET", _BASE_URL)
    flow = authorization.async_auth_flow(request)
    altered_request = await anext(flow)

    assert altered_request.headers.get("Authorization")


@freezegun.freeze_time()
async def test_valid_token_is_reused() -> None:
    request_handler = mock.AsyncMock(wraps=_valid_token)
    authorization = _create_authorization(request_handler)
    request = httpx.Request("GET", _BASE_URL)

    await anext(authorization.async_auth_flow(request))
    request_handler.assert_called_once()

    await anext(authorization.async_auth_flow(request))
    request_handler.assert_called_once()


@freezegun.freeze_time()
async def test_expired_token_is_refreshed() -> None:
    request_handler = mock.AsyncMock(wraps=_expired_token)
    authorization = _create_authorization(request_handler)
    request = httpx.Request("GET", _BASE_URL)

    await anext(authorization.async_auth_flow(request))
    await anext(authorization.async_auth_flow(request))
    assert request_handler.call_count == 2
