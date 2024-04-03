import asyncio
import datetime
import random
from collections.abc import Sequence
from typing import Any, NamedTuple

import httpx
import pydantic
from grpc import aio
from lagom.integrations.starlette import StarletteIntegration
from motor import motor_asyncio
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.rocket.service.api import (
    dependencies,
    errors,
)
from snowfall.project.junction.rocket.service.api.air import (
    repositories,
    types,
)
from snowfall.project.junction.rocket.service.api.air import (
    router as air_router,
)
from snowfall.project.junction.rocket.service.api.air.transforms import (
    transforms as air_transforms,
)
from snowfall.project.junction.rocket.service.api.car_rental import (
    router as car_rental_router,
)
from snowfall.project.junction.rocket.service.api.hotel import (
    router as hotel_router,
)
from snowfall.project.junction.rocket.service.api.middleware import (
    JunctionOneClientMiddleware,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import grpc_pb2_grpc
from snowfall.service.authentication.v1 import oauth_pb2_grpc
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.service import application, grpc_factory
from snowfall.vendor.junction_one.auth import TemporaryTokenAuth
from snowfall.vendor.junction_one.client import JunctionOneClient


class _Settings(starlette.Settings):
    authentication_address: str
    searches_address: str
    ory_jwk_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    j_one_api_key: str
    reseller_j1_credentials_mapping: dict[str, Any]
    j_one_api_base_url: str
    mongo_dsn: Sequence[pydantic.AnyUrl]
    grpc_timeout: datetime.timedelta = datetime.timedelta(seconds=45)
    reseller_pay_companies: dict[str, str]


class _Channels(NamedTuple):
    authentication: aio.Channel
    searches: aio.Channel


async def _http(app: application.Application[_Settings]) -> None:
    channels = _Channels(
        *await asyncio.gather(
            grpc_factory.make_insecure_channel(
                app,
                app.settings.authentication_address,
            ),
            grpc_factory.make_insecure_channel(
                app,
                app.settings.searches_address,
            ),
        ),
    )
    auth_backend = stdlib_auth.JWTAuthenticationBackend(
        stdlib_auth.OryAuth(
            jwk_client=jwt.AsyncJWKClient(
                jwk_url=auth_adapter.get_jwk_url(
                    app.settings.authentication_address,
                ),
                key_ttl=app.settings.ory_jwk_ttl,
            ),
            client_resolver=auth_adapter.oauth_client_resolver(
                oauth_client=oauth_pb2_grpc.OAuthServiceStub(
                    channels.authentication,
                ),
            ),
        ).get_owner_from_jwt,
    )

    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    http_client = await app.stack.enter_async_context(httpx.AsyncClient())

    container = dependencies.create_dependencies(
        grpc_timeout=app.settings.grpc_timeout,
        searches=grpc_pb2_grpc.SearchServiceStub(channels.searches),
        search_results=grpc_pb2_grpc.SearchResultServiceStub(channels.searches),
    )

    temporary_token_auth = TemporaryTokenAuth(
        api_key=app.settings.j_one_api_key,
        reseller_credentials_mapping=app.settings.reseller_j1_credentials_mapping,
    )
    container[JunctionOneClient] = JunctionOneClient(
        api_base_url=app.settings.j_one_api_base_url,
        http_client=http_client,
        auth=temporary_token_auth,
    )
    container[repositories.AbstractAirSearchRepo] = repositories.AirSearchRepo(  # type: ignore[type-abstract]
        collection=mongo.searches.air_results,
    )
    container[types.AirSearchRequestTransformer] = (  # type: ignore[type-abstract]
        air_transforms.AirSearchRequestTransformer
    )
    container[types.AirSearchResultTransformer] = (  # type: ignore[type-abstract]
        air_transforms.AirSearchResultTransformer
    )
    integration = StarletteIntegration(container)

    routes = [
        *air_router.get_routes(integration),
        *hotel_router.get_routes(integration),
        *car_rental_router.get_routes(integration),
    ]
    asgi_app = starlette.create_starlette_app(
        routes=routes,
        custom_middlewares=[
            Middleware(
                cls=authentication.AuthenticationMiddleware,
                backend=auth_backend,
                on_error=handlers.auth_error_handler,
            ),
            Middleware(
                JunctionOneClientMiddleware,
                token_auth=temporary_token_auth,
            ),
        ],
        openapi_path=filesystem.resource_path(
            "junction.rocket_api",
            "openapi.json",
        ),
    )
    asgi_app.add_exception_handler(
        cursor.CursorError,
        handlers.cursor_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.CursorError,
        handlers.cursor_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.ServiceUnavailableError,
        handlers.service_unavailable_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.UnprocessableEntityError,
        handlers.unprocessable_entity_error_handler,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=_Settings,
        ),
    )
