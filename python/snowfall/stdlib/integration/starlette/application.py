import http
import ipaddress
import pathlib
from typing import Any, Awaitable, Callable, Mapping, Optional, Sequence, cast

import uvicorn
from asgiref.typing import ASGIApplication
from starlette import applications, exceptions, requests, responses, routing, status
from starlette.middleware import Middleware

from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import handlers, middlewares
from snowfall.stdlib.integration.starlette import routes as common_routes
from snowfall.stdlib.integration.starlette import validation

ExceptionHandlerResponse = responses.Response | Awaitable[responses.Response]
ExceptionHandler = Callable[[requests.Request, Exception], ExceptionHandlerResponse]
ExceptionHandlerMapping = Mapping[Any, ExceptionHandler]


class Settings(service.Settings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80


def create_starlette_app(
    routes: Sequence[routing.BaseRoute],
    openapi_path: pathlib.Path | None,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
    validate_response: bool = True,
) -> applications.Starlette:
    stack = [Middleware(middlewares.RequestIdMiddleware)]

    if openapi_path:
        stack.append(
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(str(openapi_path)),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
                validate_response=validate_response,
            ),
        )

    return applications.Starlette(
        routes=[
            *routes,
            routing.Route("/health", common_routes.Health, name="Health"),
        ],
        middleware=[
            *stack,
            *(custom_middlewares or []),
        ],
        exception_handlers={
            status.HTTP_500_INTERNAL_SERVER_ERROR: handlers.server_error_handler,
            exceptions.HTTPException: handlers.server_error_handler,
        },
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
        ws="none",
        forwarded_allow_ips=",".join(
            [
                "*" if str(address) == "0.0.0.0" else str(address)  # nosec
                for address in allowed_proxy_ips
            ],
        ),
    )
