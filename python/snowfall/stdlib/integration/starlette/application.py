import http
import ipaddress
import os
import pathlib
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any

import uvicorn
from starlette import applications, exceptions, requests, responses, routing
from starlette.middleware import Middleware
from starlette.middleware import exceptions as exceptions_middleware

from snowfall.stdlib.integration.starlette import (
    handlers,
    middlewares,
    prometheus,
    validation,
)
from snowfall.stdlib.integration.starlette import routes as common_routes
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.service import application

ExceptionHandlerResponse = responses.Response | Awaitable[responses.Response]
ExceptionHandler = Callable[[requests.Request, Exception], ExceptionHandlerResponse]
ExceptionHandlerMapping = Mapping[Any, ExceptionHandler]


_LOGGER = stdout.get_logger()


class Settings(application.Settings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80


async def _logging_server_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.Response:
    _LOGGER.exception("An unhandled exception occurred.")

    return await handlers.server_error_handler(request, exc)


def create_starlette_app(
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

    # TODO(jyggen): pass environment from global application object
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
            Middleware(
                exceptions_middleware.ExceptionMiddleware,
                handlers={
                    Exception: _logging_server_error_handler,
                },
            ),
            *(custom_middlewares or []),
        ],
        exception_handlers={
            Exception: handlers.server_error_handler,
            exceptions.HTTPException: handlers.server_error_handler,
        },
        lifespan=lifespan,
    )


async def serve(
    starlette_app: applications.Starlette,
    settings: Settings,
) -> None:
    server = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            host=str(settings.http_address),
            loop="asyncio",
            port=settings.http_port,
            access_log=True,
            log_config=None,
            proxy_headers=True,
            server_header=False,
            ws="none",
            forwarded_allow_ips=",".join(
                [
                    "*" if str(address) == "0.0.0.0" else str(address)  # noqa: S104
                    for address in settings.forwarded_allowed_ips
                ],
            ),
        ),
    )

    server.config.setup_event_loop()

    await server.serve()
