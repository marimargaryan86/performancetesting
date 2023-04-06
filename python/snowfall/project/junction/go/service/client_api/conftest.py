import pathlib
from base64 import b64decode, b64encode
from typing import AsyncIterator, Mapping, Sequence

import httpx
import jwt as jwtlib
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth
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
from snowfall.project.junction.go.service.client_api import bootstrap, jwt
from snowfall.project.junction.go.service.client_api.routes import router
from snowfall.service.authentication.v1alpha import models_pb2 as auth_models_pb2
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import cursor, filesystem

jwt_token_version = "2.0.0"  # nosec
jwt_payload = {
    "version": jwt_token_version,
    "user_info": {
        "id": "d85ac9ee-55f1-4273-8cc8-5e9c9f326b84",
        "email": "example@example.com",
        "metadata": {
            "client_id": "d85ac9ee-55f1-4273-8cc8-5e9c9f326b84",
            "default_currency": "USD",
        },
    },
}
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


@pytest.fixture()
def authentication_client() -> auth.Client:
    return auth.DictClient(
        private_key_content=b64encode(
            jwt_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ),
        ).decode(),
        jwt_token_version=jwt_token_version,
    )


@pytest.fixture()
async def user(
    authentication_client: auth.Client,
) -> auth_models_pb2.User:
    return await authentication_client.create_user(
        email="example@example.com",
        password="myPassword",  # nosec
    )


def _create_app(  # noqa: WPS211
    authentication_client: auth.Client,
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
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(jwt_token),
    }


@pytest.fixture()
def app(  # noqa: WPS211
    authentication_client: auth.DictClient,
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
                backend=jwt.JWTAuthenticationBackend(
                    public_key=b64decode(jwt_public_key).decode(),
                    token_version=jwt_token_version,
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
