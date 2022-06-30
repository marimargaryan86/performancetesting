import http
import pathlib
from typing import Callable, Optional, Sequence, cast

from asgiref.typing import ASGIApplication
from lagom.integrations import starlette
from sentry_sdk.integrations import asgi
from starlette import applications, exceptions, routing, status
from starlette.middleware import Middleware

from snowfall.stdlib.integration.starlette import handlers, middlewares, validation

RoutesFactory = Callable[[starlette.StarletteIntegration], list[routing.Route]]


def create_asgi_app(
    dependencies: starlette.StarletteIntegration,
    routes_factory: RoutesFactory,
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> ASGIApplication:
    return cast(
        ASGIApplication,
        asgi.SentryAsgiMiddleware(
            create_starlette_app(
                custom_middlewares=custom_middlewares,
                dependencies=dependencies,
                routes_factory=routes_factory,
                openapi_path=openapi_path,
            ),
        ),
    )


def create_starlette_app(
    dependencies: starlette.StarletteIntegration,
    routes_factory: RoutesFactory,
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return applications.Starlette(
        routes=routes_factory(dependencies),
        middleware=[
            Middleware(
                middlewares.RequestIdMiddleware,
            ),
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(openapi_path),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
            *(custom_middlewares or []),
        ],
        exception_handlers={
            status.HTTP_500_INTERNAL_SERVER_ERROR: handlers.server_error_handler,
            exceptions.HTTPException: handlers.server_error_handler,
        },
    )
