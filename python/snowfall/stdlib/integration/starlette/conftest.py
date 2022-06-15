from typing import Any, AsyncIterator, Mapping, Optional, Sequence

import lagom
import pytest
from lagom.integrations import starlette
from starlette import applications, routing, testclient
from starlette.middleware import Middleware

from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence import filesystem


def _no_routes_factory(deps: starlette.StarletteIntegration) -> list[routing.Route]:
    return []


def _create_app(
    openapi_specification: Mapping[str, Any],
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        dependencies=starlette.StarletteIntegration(lagom.Container()),
        routes_factory=_no_routes_factory,
        openapi_specification=openapi_specification,
    )


@pytest.fixture()
def test_app() -> applications.Starlette:
    return _create_app(
        openapi_specification=filesystem.FileLoader().load(
            "python/snowfall/stdlib/integration/starlette/fixtures/test.json",
        ),
    )


@pytest.fixture()
async def test_client(
    test_app: applications.Starlette,
) -> AsyncIterator[testclient.TestClient]:
    with testclient.TestClient(test_app, raise_server_exceptions=False) as client:
        yield client
