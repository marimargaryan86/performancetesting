from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.plus.adapter import (
    subscribers,
)
from snowfall.project.junction.plus.service.notifications.v1 import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.plus_api import bootstrap
from snowfall.project.junction.plus.service.plus_api.routes import router
from snowfall.service.authentication.v1 import oauth_pb2_grpc
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.service import application, grpc_factory


async def _http(
    app: application.Application[bootstrap.Settings],
) -> None:
    notifications_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.notifications_address,
    )
    authentication_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.authentication_address,
    )
    asgi_app = starlette.create_starlette_app(
        custom_middlewares=[
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=stdlib_auth.JWTAuthenticationBackend(
                    stdlib_auth.OryAuth(
                        jwk_client=jwt.AsyncJWKClient(
                            jwk_url=auth_adapter.get_jwk_url(
                                app.settings.authentication_address,
                            ),
                            key_ttl=app.settings.ory_jwk_ttl,
                        ),
                        client_resolver=auth_adapter.oauth_client_resolver(
                            oauth_client=oauth_pb2_grpc.OAuthServiceStub(
                                authentication_channel,
                            ),
                        ),
                    ).get_owner_from_jwt,
                ),
                on_error=handlers.auth_error_handler,
            ),
        ],
        routes=router.get_routes(
            bootstrap.create_dependencies(
                subscribers_client=subscribers.GrpcClient(
                    subscribers=notifications_pb2_grpc.SubscriberServiceStub(
                        notifications_channel,
                    ),
                ),
            ),
        ),
        openapi_path=filesystem.resource_path(
            "junction.plus_api",
            "openapi.json",
        ),
    )

    asgi_app.add_exception_handler(
        cursor.CursorError,
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

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="junction-plus-plus-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
    )
