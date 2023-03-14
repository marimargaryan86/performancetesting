import pathlib
from typing import AsyncIterator, Mapping, Sequence

import httpx
import pytest
from starlette import applications
from starlette.middleware import Middleware

from snowfall.project.junction.adapter import errors, locations, places
from snowfall.project.junction.service.admin_api import bootstrap, router
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import cursor, filesystem


def _create_app(
    locations_client: locations.Client,
    places_client: places.Client,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    app = application.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                locations_client=locations_client,
                places_client=places_client,
            ),
        ),
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
    )
    app.add_exception_handler(cursor.CursorError, handlers.cursor_error_handler)
    app.add_exception_handler(errors.NotFoundError, handlers.not_found_error_handler)

    return app


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Authorization": "foobar",
    }


@pytest.fixture()
def app(
    locations_client: locations.Client,
    places_client: places.Client,
) -> applications.Starlette:
    return _create_app(
        locations_client=locations_client,
        places_client=places_client,
        custom_middlewares=[],
        openapi_path=filesystem.resource_path("junction.admin_api", "openapi.json"),
    )


@pytest.fixture()
async def client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        client.headers.update(dict(headers))
        yield client


@pytest.fixture()
async def unauthorized_client(
    client: httpx.AsyncClient,
) -> httpx.AsyncClient:
    client.headers.pop("Authorization")

    return client
