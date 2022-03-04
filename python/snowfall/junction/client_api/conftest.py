import http
from base64 import b64encode
from typing import AsyncIterator, Sequence

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette import applications, middleware, testclient
from starlette.middleware.authentication import AuthenticationMiddleware

from snowfall.adapter import offer_searches, places, trip_searches
from snowfall.filesystem import loaders
from snowfall.junction.client_api import bootstrap, middlewares, patch, validation

jwt_token_version = "1"  # nosec
jwt_payload = {"version": jwt_token_version, "client_id": "test"}
public_exponent = 65537
key_size = 2048
jwt_private_key = rsa.generate_private_key(
    public_exponent=public_exponent,
    key_size=key_size,
)

jwt_token = jwt.encode(
    payload=jwt_payload,
    key=jwt_private_key,  # type: ignore[arg-type]
    algorithm="RS256",
)
jwt_public_key_bytes = jwt_private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
jwt_public_key = b64encode(jwt_public_key_bytes).decode()


def _create_app(
    custom_middlewares: Sequence[middleware.Middleware],
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    offer_searches_client: offer_searches.Client,
) -> applications.Starlette:
    return bootstrap.create_app(
        custom_middlewares=custom_middlewares,
        dependencies=bootstrap.create_dependencies(
            places_client=places_client,
            trip_searches_client=trip_searches_client,
            offer_searches_client=offer_searches_client,
        ),
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(jwt_token),
    }


@pytest.fixture()
def app(
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    offer_searches_client: offer_searches.Client,
) -> applications.Starlette:
    settings = patch.AuthSettings(
        jwt_public_key=jwt_public_key,
        jwt_token_version=jwt_token_version,
    )
    return _create_app(
        custom_middlewares=[
            middleware.Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(
                    "openapi.json",
                    loaders.PkgLoader("client_api"),
                ),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
            middleware.Middleware(
                AuthenticationMiddleware,
                backend=patch.JWTAuthenticationBackend(settings),
            ),
        ],
        places_client=places_client,
        trip_searches_client=trip_searches_client,
        offer_searches_client=offer_searches_client,
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
def test_app(
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    offer_searches_client: offer_searches.Client,
) -> applications.Starlette:

    return _create_app(
        custom_middlewares=[
            middleware.Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(
                    "python/snowfall/junction/client_api/fixtures/test.json",
                    loaders.FileLoader(),
                ),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
        ],
        places_client=places_client,
        trip_searches_client=trip_searches_client,
        offer_searches_client=offer_searches_client,
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
