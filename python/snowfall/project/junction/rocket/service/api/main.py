import asyncio
import datetime
from typing import Any, NamedTuple

import lagom
from grpc import aio
from lagom.integrations.starlette import StarletteIntegration
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.go.adapter import (
    errors,
)
from snowfall.project.junction.rocket.service.api import air_search
from snowfall.service.authentication.v1 import oauth_pb2_grpc
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.service import application, grpc_factory


class _Settings(starlette.Settings):
    authentication_address: str
    ory_jwk_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    j_one_api_key: str
    reseller_j1_credentials_mapping: dict[str, Any]


class _Channels(NamedTuple):
    authentication: aio.Channel


async def _http(
    app: application.Application[_Settings],
) -> None:
    channels = _Channels(
        *await asyncio.gather(
            grpc_factory.make_insecure_channel(
                app,
                app.settings.authentication_address,
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

    container = lagom.Container()
    # TODO(paul): Add all the dependencies.

    integration = StarletteIntegration(container)

    routes = [
        integration.route(
            "/air/searches",
            air_search.AirSearch,
            name="AirSearch",
        ),
        integration.route(
            "/air/searches/{id:str}/results",
            air_search.AirSearchRetrieval,
            name="AirSearchRetrieval",
        ),
        integration.route(
            "/air/searches/{id:str}",
            air_search.AirSearchStatus,
            name="AirSearchStatus",
        ),
    ]
    asgi_app = starlette.create_starlette_app(
        routes=routes,
        custom_middlewares=[
            Middleware(
                cls=authentication.AuthenticationMiddleware,
                backend=auth_backend,
                on_error=handlers.auth_error_handler,
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
