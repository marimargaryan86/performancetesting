import http
import ipaddress
import pathlib
from typing import Callable, Optional, Sequence, cast

import uvicorn
from asgiref.typing import ASGIApplication
from lagom.integrations import starlette
from starlette import applications, exceptions, routing, status
from starlette.middleware import Middleware

from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import (
    handlers,
    middlewares,
    routes,
    validation,
)

RoutesFactory = Callable[[starlette.StarletteIntegration], list[routing.Route]]


class Settings(service.Settings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80


def create_asgi_app(
    dependencies: starlette.StarletteIntegration,
    routes_factory: RoutesFactory,
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> ASGIApplication:
    return cast(
        ASGIApplication,
        create_starlette_app(
            custom_middlewares=custom_middlewares,
            dependencies=dependencies,
            routes_factory=routes_factory,
            openapi_path=openapi_path,
        ),
    )


def create_starlette_app(
    dependencies: starlette.StarletteIntegration,
    routes_factory: RoutesFactory,
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return applications.Starlette(
        routes=[
            *routes_factory(dependencies),
            dependencies.route("/health", routes.Health, name="Health"),
        ],
        middleware=[
            Middleware(
                middlewares.RequestIdMiddleware,
            ),
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(str(openapi_path)),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
            *(custom_middlewares or []),
        ],
        exception_handlers={
            status.HTTP_500_INTERNAL_SERVER_ERROR: handlers.server_error_handler,
            exceptions.HTTPException: handlers.server_error_handler,
        },
    )


def serve(
    factory: Callable[[], ASGIApplication],
    host: str,
    port: int,
    allowed_proxy_ips: Sequence[ipaddress.IPv4Address],
) -> None:
    return uvicorn.run(
        app=factory,
        factory=True,
        host=host,
        loop="asyncio",
        port=port,
        access_log=False,
        log_config=None,
        proxy_headers=True,
        ws="none",
        forwarded_allow_ips=",".join(
            [
                "*" if str(address) == "0.0.0.0" else str(address)  # nosec
                for address in allowed_proxy_ips
            ],
        ),
    )
