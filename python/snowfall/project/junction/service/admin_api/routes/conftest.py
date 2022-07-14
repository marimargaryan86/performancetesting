import pathlib
from typing import AsyncIterator, Mapping, Optional, Sequence

import httpx
import pytest
from starlette import applications
from starlette.middleware import Middleware

from snowfall.project.junction.adapter import locations, places
from snowfall.project.junction.service.admin_api import bootstrap, router
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence import filesystem


def _create_app(
    locations_client: locations.Client,
    places_client: places.Client,
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return application.create_starlette_app(
        routes_factory=router.get_routes,
        custom_middlewares=custom_middlewares,
        dependencies=bootstrap.create_dependencies(
            locations_client=locations_client,
            places_client=places_client,
        ),
        openapi_path=openapi_path,
    )


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
