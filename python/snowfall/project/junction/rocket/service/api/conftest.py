import datetime
from collections.abc import AsyncIterator, Mapping

import httpx
import pytest
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.adapter import errors, search_results, searches
from snowfall.project.junction.rocket.service.api import dependencies, router
from snowfall.service.authentication.v1 import models_pb2 as auth_models_pb2
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.persistence import filesystem


async def mock_jwt_to_reseller_id(token: str) -> str:
    return fixtures.RESELLER_ID


@pytest.fixture()
def search_results_client() -> search_results.DictClient:
    return search_results.DictClient(fixtures.get_search_results())


@pytest.fixture()
def searches_client() -> searches.DictClient:
    return searches.DictClient(fixtures.get_searches())


@pytest.fixture()
def app(
    search_results_client: search_results.Client,
    searches_client: searches.Client,
) -> applications.Starlette:
    asgi_app = application.create_starlette_app(
        routes=router.get_routes(
            dependencies.create_dependencies(
                search_results_client=search_results_client,
                searches_client=searches_client,
            ),
        ),
        openapi_path=filesystem.resource_path("junction.rocket_api", "openapi.json"),
        custom_middlewares=[
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=stdlib_auth.JWTAuthenticationBackend(
                    jwt_to_user_id=mock_jwt_to_reseller_id,
                ),
                on_error=handlers.auth_error_handler,
            ),
        ],
        security_headers=False,
    )

    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.UnprocessableEntityError,
        handlers.unprocessable_entity_error_handler,
    )

    return asgi_app


@pytest.fixture()
def authentication_client() -> auth_adapter.Client:
    return auth_adapter.DictClient()


@pytest.fixture()
async def user(
    authentication_client: auth_adapter.Client,
) -> auth_models_pb2.User:
    user = await authentication_client.create_user(
        email="example@example.com",
        password="myPassword",
    )

    user.metadata["client_id"] = "foo"
    user.metadata["default_currency"] = "bar"

    return user


@pytest.fixture()
async def unauthorized_client(
    client: httpx.AsyncClient,
) -> httpx.AsyncClient:
    client.headers.pop("Authorization")

    return client


@pytest.fixture()
def jwt_token(user: auth_models_pb2.User) -> str:
    return jwt.Encoder().encode(
        auth_adapter.JWTFactory(ttl=datetime.timedelta(hours=1)).from_user(user),
    )


@pytest.fixture()
def headers(jwt_token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(jwt_token),
    }


@pytest.fixture()
async def client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),  # type: ignore[arg-type]
        base_url="https://example.com",
    ) as client:
        client.headers.update(dict(headers))

        yield client
