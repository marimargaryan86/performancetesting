import pathlib
from base64 import b64decode, b64encode
from typing import AsyncIterator, Mapping, Optional, Sequence

import httpx
import jwt as jwtlib
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.project.junction.adapter import (
    legs,
    locations,
    offer_searches,
    offers,
    orders,
    places,
    schedules,
    segments,
    trip_searches,
    trips,
)
from snowfall.project.junction.service.client_api import bootstrap, jwt
from snowfall.project.junction.service.client_api.routes import router
from snowfall.stdlib.integration.starlette import application, handlers
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
    legs_client: legs.Client,
    locations_client: locations.Client,
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    orders_client: orders.Client,
    offers_client: offers.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return application.create_starlette_app(
        routes_factory=router.get_routes,
        custom_middlewares=custom_middlewares,
        dependencies=bootstrap.create_dependencies(
            legs_client=legs_client,
            locations_client=locations_client,
            places_client=places_client,
            trip_searches_client=trip_searches_client,
            trips_client=trips_client,
            orders_client=orders_client,
            offers_client=offers_client,
            offer_searches_client=offer_searches_client,
            segments_client=segments_client,
            schedules_client=schedules_client,
        ),
        openapi_path=openapi_path,
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(jwt_token),
    }


@pytest.fixture()
def app(  # noqa: WPS211
    legs_client: legs.Client,
    locations_client: locations.Client,
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    orders_client: orders.Client,
    offers_client: offers.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
) -> applications.Starlette:
    return _create_app(
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
        trip_searches_client=trip_searches_client,
        trips_client=trips_client,
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
