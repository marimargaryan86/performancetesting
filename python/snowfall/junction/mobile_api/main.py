import http
from typing import Callable, cast

import uvicorn
from asgiref.typing import ASGIApplication
from sentry_sdk.integrations import asgi
from starlette.middleware import Middleware

from snowfall.junction.mobile_api import bootstrap
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import middlewares, validation
from snowfall.stdlib.persistence import filesystem


def _factory() -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        return cast(
            ASGIApplication,
            asgi.SentryAsgiMiddleware(
                bootstrap.create_app(
                    dependencies=bootstrap.create_dependencies(),
                    custom_middlewares=[
                        Middleware(
                            middlewares.ValidationMiddleware,
                            validator=validation.Validator(
                                "openapi.json",
                                filesystem.PkgLoader("mobile_api"),
                            ),
                            excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
                        ),
                    ],
                ),
            ),
        )

    return decorator


def _serve(app: service.Application[bootstrap.Settings]) -> None:
    uvicorn.run(
        app=_factory(),
        factory=True,
        host=str(app.settings.http_address),
        loop="asyncio",
        port=app.settings.http_port,
        access_log=False,
        log_config=None,
        proxy_headers=True,
        forwarded_allow_ips=[
            "*" if str(address) == "0.0.0.0" else str(address)  # nosec
            for address in app.settings.forwarded_allowed_ips
        ],
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="client-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
