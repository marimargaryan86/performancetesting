import http
import ipaddress
import os
import pathlib
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any, cast

import uvicorn
from asgiref.typing import ASGIApplication
from starlette import applications, exceptions, requests, responses, routing, status
from starlette.middleware import Middleware, errors

from snowfall.stdlib.integration.starlette import (
    handlers,
    middlewares,
    prometheus,
    validation,
)
from snowfall.stdlib.integration.starlette import routes as common_routes
from snowfall.stdlib.service import application

ExceptionHandlerResponse = responses.Response | Awaitable[responses.Response]
ExceptionHandler = Callable[[requests.Request, Exception], ExceptionHandlerResponse]
ExceptionHandlerMapping = Mapping[Any, ExceptionHandler]


class Settings(application.Settings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80


def create_starlette_app(  # noqa: WPS211
    *,
    routes: Sequence[routing.BaseRoute],
    openapi_path: pathlib.Path | None,
    custom_middlewares: Sequence[Middleware] | None = None,
    security_headers: bool = True,
    lifespan: Any = None,
) -> applications.Starlette:
    stack = [
        Middleware(prometheus.Middleware),
        Middleware(middlewares.RequestIdMiddleware),
    ]

    if security_headers:
        stack.append(Middleware(middlewares.SecurityHeadersMiddleware))

    validation_mode = middlewares.ValidationMode.disabled

    # @todo: pass environment from global application object
    match os.environ.get("ENV_NAME", "local"):
        case "local":
            validation_mode = middlewares.ValidationMode.eager
        case "development":
            validation_mode = middlewares.ValidationMode.lazy

    if openapi_path:
        stack.append(
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(openapi_path),
                excluded_status_codes={
                    http.HTTPStatus.METHOD_NOT_ALLOWED,
                    http.HTTPStatus.INTERNAL_SERVER_ERROR,
                },
                validation_mode=validation_mode,
            ),
        )

    return applications.Starlette(
        routes=[
            routing.Route("/health", common_routes.Health, name="Health"),
            *routes,
        ],
        middleware=[
            *stack,
            *(custom_middlewares or []),
            Middleware(
                errors.ServerErrorMiddleware,
                handler=handlers.server_error_handler,
            ),
        ],
        exception_handlers={
            status.HTTP_500_INTERNAL_SERVER_ERROR: handlers.server_error_handler,
            exceptions.HTTPException: handlers.server_error_handler,
        },
        lifespan=lifespan,
    )


def serve(
    factory: Callable[[], applications.Starlette],
    host: str,
    port: int,
    allowed_proxy_ips: Sequence[ipaddress.IPv4Address],
) -> None:
    return uvicorn.run(
        app=cast(ASGIApplication, factory),
        factory=True,
        host=host,
        loop="asyncio",
        port=port,
        access_log=False,
        log_config=None,
        proxy_headers=True,
        server_header=False,
        ws="none",
        forwarded_allow_ips=",".join(
            [
                "*" if str(address) == "0.0.0.0" else str(address)  # noqa: S104
                for address in allowed_proxy_ips
            ],
        ),
    )
