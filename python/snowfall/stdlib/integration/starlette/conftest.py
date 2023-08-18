import pathlib
from collections.abc import AsyncIterator, Sequence
from typing import Any

import httpx
import pytest
from starlette import applications
from starlette.middleware import Middleware

from snowfall.stdlib.integration.starlette import application


def _create_app(
    openapi_path: pathlib.Path | None,
    custom_middlewares: Sequence[Middleware] | None = None,
    *,
    validate_response: bool = True,
) -> applications.Starlette:
    return application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        routes=[],
        openapi_path=openapi_path,
        validate_response=validate_response,
    )


@pytest.fixture(
    params=[
        "python/snowfall/stdlib/integration/starlette/fixtures/test.json",
        "python/snowfall/stdlib/integration/starlette/fixtures/test.3.1.json",
    ],
    ids=["3.0", "3.1"],
)
def test_app(request: Any) -> applications.Starlette:
    return _create_app(openapi_path=pathlib.Path(request.param))


@pytest.fixture()
def test_app_without_spec() -> applications.Starlette:
    return _create_app(openapi_path=None)


@pytest.fixture(
    params=[
        "python/snowfall/stdlib/integration/starlette/fixtures/test.json",
        "python/snowfall/stdlib/integration/starlette/fixtures/test.3.1.json",
    ],
    ids=["3.0", "3.1"],
)
def test_app_without_response_validation(
    request: Any,
) -> applications.Starlette:
    return _create_app(
        openapi_path=pathlib.Path(request.param),
        validate_response=False,
    )


@pytest.fixture()
async def test_client(
    test_app: applications.Starlette,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        base_url="https://example.com",
        transport=httpx.ASGITransport(
            app=test_app,  # type: ignore[arg-type]
            raise_app_exceptions=False,
        ),
    ) as client:
        yield client


@pytest.fixture()
async def test_client_without_spec(
    test_app_without_spec: applications.Starlette,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        base_url="https://example.com",
        transport=httpx.ASGITransport(
            app=test_app_without_spec,  # type: ignore[arg-type]
            raise_app_exceptions=False,
        ),
    ) as client:
        yield client


@pytest.fixture()
async def test_client_without_response_validation(
    test_app_without_response_validation: applications.Starlette,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        base_url="https://example.com",
        transport=httpx.ASGITransport(
            app=test_app_without_response_validation,  # type: ignore[arg-type]
            raise_app_exceptions=False,
        ),
    ) as client:
        yield client
