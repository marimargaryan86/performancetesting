import datetime
from collections.abc import AsyncIterator, Mapping

import grpc
import grpc_testing
import httpx
import lagom
import pytest
import pytest_mock
from lagom.integrations.starlette import StarletteIntegration
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.conftest import mongomock_motor  # type: ignore [attr-defined]
from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.service.api import errors, fakes
from snowfall.project.junction.rocket.service.api.air import endpoints as routes
from snowfall.project.junction.rocket.service.api.air.repositories import AirSearchRepo
from snowfall.project.junction.rocket.service.api.air.types import (
    AbstractAirSearchRepo,
    AirSearchRequestTransformer,
    AirSearchResultTransformer,
)
from snowfall.project.junction.rocket.service.api.car_rental import (
    router as car_rental_router,
)
from snowfall.project.junction.rocket.service.api.hotel import router as hotel_router
from snowfall.project.junction.rocket.service.api.hotel import (
    transformers as hotel_transformers,
)
from snowfall.project.junction.rocket.service.api.hotel import types as hotel_types
from snowfall.project.junction.rocket.service.api.hotel.repositories import (
    HotelSearchRepo,
)
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
from snowfall.vendor.junction_one.client import JunctionOneClient


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def junction_one_client(http_client: httpx.AsyncClient) -> JunctionOneClient:
    return JunctionOneClient(api_base_url="https://localhost/", http_client=http_client)


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
def container(
    searches: grpc_pb2_grpc.SearchServiceStub,
    search_results: grpc_pb2_grpc.SearchResultServiceStub,
    junction_one_client: JunctionOneClient,
    air_search_repo: AirSearchRepo,
    hotel_search_repo: HotelSearchRepo,
) -> lagom.Container:
    container = lagom.Container()

    container[datetime.timedelta] = datetime.timedelta(seconds=45)
    container[grpc_pb2_grpc.SearchServiceStub] = searches
    container[grpc_pb2_grpc.SearchResultServiceStub] = search_results
    container[JunctionOneClient] = junction_one_client
    container[AbstractAirSearchRepo] = air_search_repo  # type: ignore[type-abstract]
    container[AirSearchRequestTransformer] = fakes.FakeAirSearchRequestTransformer  # type: ignore[type-abstract]
    container[AirSearchResultTransformer] = fakes.FakeAirSearchResultTransformer  # type: ignore[type-abstract]
    container[hotel_types.AbstractHotelSearchRepo] = hotel_search_repo  # type: ignore[type-abstract]
    container[hotel_types.HotelSearchRequestTransformer] = (  # type: ignore[type-abstract]
        hotel_transformers.HotelSearchRequestTransformer
    )
    container[hotel_types.HotelSearchResultTransformer] = (  # type: ignore[type-abstract]
        hotel_transformers.HotelSearchResultTransformer
    )

    return container


@pytest.fixture()
def app(container: lagom.Container) -> applications.Starlette:
    integration = StarletteIntegration(container)
    route_list = [
        *car_rental_router.get_routes(integration),
        *hotel_router.get_routes(integration),
        integration.route("/air/searches", routes.AirSearch, name="AirSearch"),
        integration.route(
            "/air/searches/{id}/results",
            routes.AirSearchRetrieval,
            name="AirSearchRetrieval",
        ),
        integration.route(
            "/air/searches/{id}",
            routes.AirSearchStatus,
            name="AirSearchStatus",
        ),
    ]
    asgi_app = application.create_starlette_app(
        routes=route_list,
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
        "Content-Type": "application/vnd.api+json",
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


@pytest.fixture()
async def mock_collection() -> mongomock_motor.AsyncMongoMockCollection:
    return mongomock_motor.AsyncMongoMockClient()["db"]["collection"]


@pytest.fixture()
async def air_search_repo(
    mock_collection: mongomock_motor.AsyncMongoMockCollection,
) -> AirSearchRepo:
    return AirSearchRepo(collection=mock_collection)


@pytest.fixture()
async def hotel_search_repo(
    mock_collection: mongomock_motor.AsyncMongoMockCollection,
) -> HotelSearchRepo:
    return HotelSearchRepo(collection=mock_collection)
