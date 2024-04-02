import datetime
from collections.abc import AsyncIterator, Mapping

import grpc
import grpc_testing
import httpx
import pytest
import pytest_mock
from lagom.integrations import starlette
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.service.api import dependencies, errors
from snowfall.project.junction.rocket.service.api.car_rental import router
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
)
from snowfall.service.authentication.v1 import models_pb2 as auth_models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.persistence import filesystem


async def mock_jwt_to_reseller_id(token: str) -> str:
    return fixtures.RESELLER_ID


@pytest.fixture()
def searches(mocker: pytest_mock.MockerFixture) -> grpc_pb2_grpc.SearchServiceStub:
    searches = grpc_pb2_grpc.SearchServiceStub(
        grpc_testing.channel([], grpc_testing.strict_real_time()),
    )

    mocker.patch.object(
        searches,
        "EnqueueSearch",
        side_effect=_create_search,
    )
    mocker.patch.object(
        searches,
        "GetSearch",
        side_effect=_get_search,
    )

    return searches


@pytest.fixture()
def search_results(
    mocker: pytest_mock.MockerFixture,
) -> grpc_pb2_grpc.SearchResultServiceStub:
    search_results = grpc_pb2_grpc.SearchResultServiceStub(
        grpc_testing.channel([], grpc_testing.strict_real_time()),
    )

    mocker.patch.object(
        search_results,
        "ListSearchResults",
        side_effect=_get_search_results,
    )

    return search_results


@pytest.fixture()
def app(
    searches: grpc_pb2_grpc.SearchServiceStub,
    search_results: grpc_pb2_grpc.SearchResultServiceStub,
) -> applications.Starlette:
    asgi_app = application.create_starlette_app(
        routes=router.get_routes(
            starlette.StarletteIntegration(
                dependencies.create_dependencies(
                    grpc_timeout=datetime.timedelta(seconds=45),
                    searches=searches,
                    search_results=search_results,
                ),
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


async def _create_search(
    request: grpc_pb2.EnqueueSearchRequest,
    timeout: datetime.datetime,
) -> grpc_pb2.EnqueueSearchResponse:
    return grpc_pb2.EnqueueSearchResponse(
        search=fixtures.generate_search(string.uuid()),
    )


async def _get_search(
    request: grpc_pb2.GetSearchRequest,
    timeout: datetime.datetime,
) -> grpc_pb2.GetSearchResponse:
    if request.id not in fixtures.SEARCHES:
        raise grpc.aio.AioRpcError(
            code=grpc.StatusCode.NOT_FOUND,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        )

    return grpc_pb2.GetSearchResponse(search=fixtures.generate_search(request.id))


async def _get_search_results(
    request: grpc_pb2.ListSearchResultsRequest,
    timeout: datetime.datetime,
) -> grpc_pb2.ListSearchResultsResponse:
    if request.search_id not in fixtures.SEARCHES:
        raise grpc.aio.AioRpcError(
            code=grpc.StatusCode.NOT_FOUND,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        )

    return grpc_pb2.ListSearchResultsResponse(
        search_results=fixtures.get_search_results(),
    )
