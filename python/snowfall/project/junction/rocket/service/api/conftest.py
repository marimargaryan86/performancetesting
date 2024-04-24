import datetime
from collections.abc import AsyncIterator, Mapping

import grpc
import grpc_testing
import httpx
import lagom
import pytest
import pytest_mock
from lagom.integrations.starlette import StarletteIntegration
from motor import motor_asyncio
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.service.api import errors, includes
from snowfall.project.junction.rocket.service.api.air import (
    router as air_router,
)
from snowfall.project.junction.rocket.service.api.air.repositories import (
    AirSearchRequestRepository,
    AirSearchResultRepository,
)
from snowfall.project.junction.rocket.service.api.air.transforms import (
    transforms as air_transforms,
)
from snowfall.project.junction.rocket.service.api.air.types import (
    AirSearchRequestTransformer,
    AirSearchResultTransformer,
)
from snowfall.project.junction.rocket.service.api.car_rental import (
    router as car_rental_router,
)
from snowfall.project.junction.rocket.service.api.ferry import (
    router as ferry_router,
)
from snowfall.project.junction.rocket.service.api.hotel import (
    router as hotel_router,
)
from snowfall.project.junction.rocket.service.api.hotel import (
    transformers as hotel_transformers,
)
from snowfall.project.junction.rocket.service.api.hotel import types as hotel_types
from snowfall.project.junction.rocket.service.api.hotel.repositories import (
    HotelRoomsSearchRepository,
    HotelSearchRepository,
)
from snowfall.project.junction.rocket.service.api.multi_modality import (
    endpoints as multi_modal_endpoints,
)
from snowfall.project.junction.rocket.service.api.multi_modality import (
    repository as multi_modal_repository,
)
from snowfall.project.junction.rocket.service.api.places import (
    router as places_router,
)
from snowfall.project.junction.rocket.service.api.rail import (
    router as rail_router,
)
from snowfall.project.junction.rocket.service.places.v1alpha import (
    places_pb2,
    places_pb2_grpc,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
)
from snowfall.service.authentication.v1 import models_pb2 as auth_models_pb2
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import memory
from snowfall.stdlib.v1 import amqp_pb2
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
def places_stub(mocker: pytest_mock.MockerFixture) -> places_pb2_grpc.PlacesServiceStub:
    places = places_pb2_grpc.PlacesServiceStub(
        grpc_testing.channel([], grpc_testing.strict_real_time()),
    )

    mocker.patch.object(
        places,
        "GetPlace",
        side_effect=_get_place,
    )
    mocker.patch.object(
        places,
        "GetPlaceByIata",
        side_effect=_get_place_by_iata,
    )
    mocker.patch.object(
        places,
        "ListPlaces",
        side_effect=_list_places,
    )

    return places


@pytest.fixture()
def container(
    searches: grpc_pb2_grpc.SearchServiceStub,
    search_results: grpc_pb2_grpc.SearchResultServiceStub,
    places_stub: places_pb2_grpc.PlacesServiceStub,
    junction_one_client: JunctionOneClient,
    air_search_repo: AirSearchResultRepository,
    air_search_request_repo: AirSearchRequestRepository,
    hotel_search_repo: HotelSearchRepository,
    hotel_rooms_search_repo: HotelRoomsSearchRepository,
) -> lagom.Container:
    container = lagom.Container()

    container[datetime.timedelta] = datetime.timedelta(seconds=45)
    container[grpc_pb2_grpc.SearchServiceStub] = searches
    container[grpc_pb2_grpc.SearchResultServiceStub] = search_results
    container[places_pb2_grpc.PlacesServiceStub] = places_stub
    container[JunctionOneClient] = junction_one_client
    container[AirSearchResultRepository] = air_search_repo
    container[AirSearchRequestRepository] = air_search_request_repo
    container[AirSearchRequestTransformer] = (  # type: ignore[type-abstract]
        air_transforms.AirSearchRequestTransformer
    )
    container[AirSearchResultTransformer] = (  # type: ignore[type-abstract]
        air_transforms.AirSearchResultTransformer
    )
    container[HotelSearchRepository] = hotel_search_repo
    container[hotel_types.HotelSearchRequestTransformer] = (  # type: ignore[type-abstract]
        hotel_transformers.HotelSearchRequestTransformer
    )
    container[hotel_types.HotelSearchResultTransformer] = (  # type: ignore[type-abstract]
        hotel_transformers.HotelSearchResultTransformer
    )
    container[HotelRoomsSearchRepository] = hotel_rooms_search_repo

    includes.register_resolvers(
        air_results_repo=air_search_repo,
    )

    return container


@pytest.fixture()
async def suggestion_search_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> multi_modal_repository.SuggestionSearchRepository:
    return multi_modal_repository.SuggestionSearchRepository(
        collection=mongo_client["test"]["suggestions_search"],
        ttl=datetime.timedelta(minutes=30),
    )


@pytest.fixture()
async def suggestion_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> multi_modal_repository.SuggestionRepository:
    return multi_modal_repository.SuggestionRepository(
        collection=mongo_client["test"]["suggestions"],
        ttl=datetime.timedelta(minutes=30),
    )


@pytest.fixture()
def suggestions_searches(
    places_stub: places_pb2_grpc.PlacesServiceStub,
    suggestion_search_repository: multi_modal_repository.SuggestionSearchRepository,
    suggestion_repository: multi_modal_repository.SuggestionRepository,
) -> multi_modal_endpoints.SuggestionSearches:
    return multi_modal_endpoints.SuggestionSearches(
        _places=places_stub,
        _repository=suggestion_search_repository,
        _producer=memory.Producer(),
        _suggestions=suggestion_repository,
    )


@pytest.fixture()
def suggestions(
    suggestion_repository: multi_modal_repository.SuggestionRepository,
) -> multi_modal_endpoints.Suggestions:
    return multi_modal_endpoints.Suggestions(
        _repository=suggestion_repository,
    )


@pytest.fixture()
def app(
    container: lagom.Container,
    suggestions: multi_modal_endpoints.Suggestions,
    suggestions_searches: multi_modal_endpoints.SuggestionSearches,
) -> applications.Starlette:
    integration = StarletteIntegration(container)
    route_list = [
        *air_router.get_routes(integration),
        *car_rental_router.get_routes(integration),
        *ferry_router.get_routes(integration),
        *hotel_router.get_routes(integration),
        *places_router.get_routes(integration),
        *rail_router.get_routes(integration),
        *multi_modal_endpoints.get_routes(
            suggestions=suggestions,
            suggestion_searches=suggestions_searches,
        ),
    ]
    asgi_app = application.create_starlette_app(
        routes=route_list,
        openapi_path=filesystem.resource_path("junction.rocket_api", "openapi.yaml"),
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
    timeout: datetime.datetime | None = None,
) -> grpc_pb2.EnqueueSearchResponse:
    return grpc_pb2.EnqueueSearchResponse(
        search=fixtures.generate_search(
            fixtures.SEARCHES[0],
            request.search,
            amqp_pb2.Trackable.STATUS_PENDING,
        ),
    )


async def _get_search(
    request: grpc_pb2.GetSearchRequest,
    timeout: datetime.datetime | None = None,
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
    timeout: datetime.datetime | None = None,
) -> grpc_pb2.ListSearchResultsResponse:
    if request.search_id not in fixtures.SEARCHES:
        raise grpc.aio.AioRpcError(
            code=grpc.StatusCode.NOT_FOUND,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        )

    return grpc_pb2.ListSearchResultsResponse(
        search_results=fixtures.generate_search_results(request.search_id),
    )


async def _get_place(
    request: places_pb2.GetPlaceRequest,
    timeout: datetime.datetime | None = None,
) -> places_pb2.GetPlaceResponse:
    if request.id not in fixtures.PLACES:
        raise grpc.aio.AioRpcError(
            code=grpc.StatusCode.NOT_FOUND,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        )

    return places_pb2.GetPlaceResponse(place=fixtures.get_place())


async def _get_place_by_iata(
    request: places_pb2.GetPlaceByIataRequest,
    timeout: datetime.datetime,
) -> places_pb2.GetPlaceByIataResponse:
    if request.iata not in fixtures.PLACE_IATAS:
        raise grpc.aio.AioRpcError(
            code=grpc.StatusCode.NOT_FOUND,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        )

    return places_pb2.GetPlaceByIataResponse(place=fixtures.get_place())


async def _list_places(
    request: places_pb2.ListPlacesRequest,
    timeout: datetime.datetime,
) -> places_pb2.ListPlacesResponse:
    if request.filters.name not in fixtures.PLACE_NAMES:
        raise grpc.aio.AioRpcError(
            code=grpc.StatusCode.NOT_FOUND,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        )

    return places_pb2.ListPlacesResponse(
        places=[fixtures.get_place()],
        next_page_token="",
    )


@pytest.fixture()
async def air_search_request_repo(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> AirSearchRequestRepository:
    return AirSearchRequestRepository(collection=mongo_client["db"]["air_request"])


@pytest.fixture()
async def air_search_repo(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> AirSearchResultRepository:
    return AirSearchResultRepository(collection=mongo_client["db"]["air_search"])


@pytest.fixture()
async def hotel_search_repo(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> HotelSearchRepository:
    return HotelSearchRepository(collection=mongo_client["db"]["hotel_search"])


@pytest.fixture()
async def hotel_rooms_search_repo(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> HotelRoomsSearchRepository:
    return HotelRoomsSearchRepository(collection=mongo_client["db"]["hotel_rooms"])
