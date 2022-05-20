import http
from typing import AsyncIterator, Sequence

import pytest
from starlette import applications, exceptions, status, testclient
from starlette.middleware import Middleware

from snowfall.stdlib.integration.starlette import handlers, middlewares, validation
from snowfall.stdlib.persistence import filesystem


def _create_app(
    custom_middlewares: Sequence[Middleware],
) -> applications.Starlette:
    app = applications.Starlette(
        middleware=custom_middlewares,
    )
    app.add_exception_handler(exceptions.HTTPException, handlers.exception_handler)
    app.add_exception_handler(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        handlers.error_handler,
    )

    return app


@pytest.fixture()
def test_app() -> applications.Starlette:
    return _create_app(
        custom_middlewares=[
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(
                    "python/snowfall/stdlib/integration/starlette/fixtures/test.json",
                    filesystem.FileLoader(),
                ),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
        ],
    )


@pytest.fixture()
async def test_client(
    test_app: applications.Starlette,
) -> AsyncIterator[testclient.TestClient]:
    with testclient.TestClient(test_app, raise_server_exceptions=False) as client:
        yield client
