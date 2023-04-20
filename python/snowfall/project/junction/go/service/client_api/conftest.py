import datetime
import pathlib
from typing import AsyncIterator, Mapping, Sequence

import httpx
import pytest
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.go.adapter import (
    errors,
    legs,
    locations,
    offer_searches,
    offers,
    orders,
    places,
    price_quotes,
    schedules,
    segments,
    trip_candidate_searches,
    trip_candidates,
    trip_searches,
    trips,
)
from snowfall.project.junction.go.service.client_api import (
    authentication as authentication_backends,
)
from snowfall.project.junction.go.service.client_api import bootstrap, router
from snowfall.service.authentication import auth
from snowfall.service.authentication.v1alpha import models_pb2 as auth_models_pb2
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import cursor, filesystem


@pytest.fixture()
def authentication_client() -> auth_adapter.Client:
    return auth_adapter.DictClient()


@pytest.fixture()
async def user(
    authentication_client: auth_adapter.Client,
) -> auth_models_pb2.User:
    user = await authentication_client.create_user(
        email="example@example.com",
        password="myPassword",  # nosec
    )

    user.metadata["client_id"] = "foo"
    user.metadata["default_currency"] = "bar"

    return user


def _create_app(  # noqa: WPS211
    authentication_client: auth_adapter.Client,
    legs_client: legs.Client,
    locations_client: locations.Client,
    places_client: places.Client,
    price_quotes_client: price_quotes.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    trip_candidate_searches_client: trip_candidate_searches.Client,
    trip_candidates_client: trip_candidates.Client,
    orders_client: orders.Client,
    offers_client: offers.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    app = application.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                authentication_client=authentication_client,
                legs_client=legs_client,
                locations_client=locations_client,
                places_client=places_client,
                price_quotes_client=price_quotes_client,
                trip_searches_client=trip_searches_client,
                trips_client=trips_client,
                trip_candidate_searches_client=trip_candidate_searches_client,
                trip_candidates_client=trip_candidates_client,
                orders_client=orders_client,
                offers_client=offers_client,
                offer_searches_client=offer_searches_client,
                segments_client=segments_client,
                schedules_client=schedules_client,
            ),
        ),
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
    )
    app.add_exception_handler(cursor.CursorError, handlers.cursor_error_handler)
    app.add_exception_handler(errors.NotFoundError, handlers.not_found_error_handler)

    return app


@pytest.fixture()
def jwt_token(user: auth_models_pb2.User) -> str:
    return jwt.Encoder().encode(
        auth.JWTFactory(ttl=datetime.timedelta(hours=1)).from_user(user),
    )


@pytest.fixture()
def headers(jwt_token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(jwt_token),
    }


@pytest.fixture()
def app(  # noqa: WPS211
    authentication_client: auth_adapter.DictClient,
    legs_client: legs.Client,
    locations_client: locations.Client,
    places_client: places.Client,
    price_quotes_client: price_quotes.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    trip_candidate_searches_client: trip_candidate_searches.Client,
    trip_candidates_client: trip_candidates.Client,
    orders_client: orders.Client,
    offers_client: offers.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
) -> applications.Starlette:
    return _create_app(
        authentication_client=authentication_client,
        custom_middlewares=[
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=authentication_backends.JWTAuthenticationBackend(
                    jwt.Decoder(),
                    jwt_version="1.0.0",
                ),
                on_error=handlers.auth_error_handler,
            ),
        ],
        legs_client=legs_client,
        locations_client=locations_client,
        places_client=places_client,
        price_quotes_client=price_quotes_client,
        trip_searches_client=trip_searches_client,
        trips_client=trips_client,
        trip_candidate_searches_client=trip_candidate_searches_client,
        trip_candidates_client=trip_candidates_client,
        orders_client=orders_client,
        offers_client=offers_client,
        offer_searches_client=offer_searches_client,
        segments_client=segments_client,
        schedules_client=schedules_client,
        openapi_path=filesystem.resource_path("junction.client_api", "openapi.json"),
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
