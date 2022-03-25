import http
from base64 import b64decode, b64encode
from typing import AsyncIterator, Sequence

import jwt as jwtlib
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette import applications, testclient
from starlette.middleware import Middleware, authentication

from snowfall.adapter import (
    offer_searches,
    places,
    schedules,
    segments,
    trip_searches,
    trips,
)
from snowfall.junction.client_api import (
    bootstrap,
    handlers,
    jwt,
    middlewares,
    validation,
)
from snowfall.stdlib.persistence import filesystem

jwt_token_version = "1"  # nosec
jwt_payload = {"version": jwt_token_version, "client_id": "test"}
public_exponent = 65537
key_size = 2048
jwt_private_key = rsa.generate_private_key(
    public_exponent=public_exponent,
    key_size=key_size,
)

jwt_token = jwtlib.encode(
    payload=jwt_payload,
    key=jwt_private_key,  # type: ignore[arg-type]
    algorithm="RS256",
)
jwt_public_key_bytes = jwt_private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
jwt_public_key = b64encode(jwt_public_key_bytes).decode()


def _create_app(  # noqa: WPS211
    custom_middlewares: Sequence[Middleware],
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
) -> applications.Starlette:
    return bootstrap.create_app(
        custom_middlewares=custom_middlewares,
        dependencies=bootstrap.create_dependencies(
            places_client=places_client,
            trip_searches_client=trip_searches_client,
            trips_client=trips_client,
            offer_searches_client=offer_searches_client,
            segments_client=segments_client,
            schedules_client=schedules_client,
        ),
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(jwt_token),
    }


@pytest.fixture()
def app(  # noqa: WPS211
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
) -> applications.Starlette:
    return _create_app(
        custom_middlewares=[
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(
                    "openapi.json",
                    filesystem.PkgLoader("client_api"),
                ),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=jwt.JWTAuthenticationBackend(
                    public_key=b64decode(jwt_public_key).decode(),
                    token_version=jwt_token_version,
                ),
                on_error=handlers.auth_error_handler,
            ),
        ],
        places_client=places_client,
        trip_searches_client=trip_searches_client,
        trips_client=trips_client,
        offer_searches_client=offer_searches_client,
        segments_client=segments_client,
        schedules_client=schedules_client,
    )


@pytest.fixture()
def client(
    app: applications.Starlette,
    headers: dict[str, str],
) -> testclient.TestClient:
    client = testclient.TestClient(app)
    client.headers.update(headers)

    return client


@pytest.fixture()
def unauthorized_client(
    client: testclient.TestClient,
) -> testclient.TestClient:
    client.headers.pop("Authorization")

    return client


@pytest.fixture()
def test_app(  # noqa: WPS211
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
) -> applications.Starlette:
    return _create_app(
        custom_middlewares=[
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(
                    "python/snowfall/junction/client_api/fixtures/test.json",
                    filesystem.FileLoader(),
                ),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
        ],
        places_client=places_client,
        trip_searches_client=trip_searches_client,
        trips_client=trips_client,
        offer_searches_client=offer_searches_client,
        segments_client=segments_client,
        schedules_client=schedules_client,
    )


@pytest.fixture()
async def test_client(
    test_app: applications.Starlette,
) -> AsyncIterator[testclient.TestClient]:
    with testclient.TestClient(test_app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture()
async def test_error_client(
    test_app: applications.Starlette,
) -> AsyncIterator[testclient.TestClient]:
    with testclient.TestClient(test_app) as client:
        yield client
