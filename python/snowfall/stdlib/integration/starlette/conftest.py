import pathlib
from typing import AsyncIterator, Optional, Sequence

import httpx
import lagom
import pytest
from lagom.integrations import starlette
from starlette import applications, routing
from starlette.middleware import Middleware

from snowfall.stdlib.integration.starlette import application


def _no_routes_factory(deps: starlette.StarletteIntegration) -> list[routing.Route]:
    return []


def _create_app(
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        dependencies=starlette.StarletteIntegration(lagom.Container()),
        routes_factory=_no_routes_factory,
        openapi_path=openapi_path,
    )


@pytest.fixture()
def test_app() -> applications.Starlette:
    return _create_app(
        openapi_path=pathlib.Path(
            "python/snowfall/stdlib/integration/starlette/fixtures/test.json",
        ),
    )


@pytest.fixture()
async def test_client(
    test_app: applications.Starlette,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        base_url="https://example.com",
        transport=httpx.ASGITransport(app=test_app, raise_app_exceptions=False),
    ) as client:
        yield client
