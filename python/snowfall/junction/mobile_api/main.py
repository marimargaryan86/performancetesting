import http
import random
from typing import Callable, cast

import aioredis
import uvicorn
from asgiref.typing import ASGIApplication
from sentry_sdk.integrations import asgi
from starlette.middleware import Middleware

from snowfall.junction.mobile_api import bootstrap, repository
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import middlewares, validation
from snowfall.stdlib.persistence import filesystem, redis
from snowfall.vendor.junction import client


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        places_repository = repository.PlacesRepository(
            junction_client=client.JunctionClient(
                api_url=random.choice(app.settings.junction_api_address),  # nosec
                token=app.settings.junction_api_token,
            ),
            redis_client=redis.Client[str](
                aioredis.from_url(
                    random.choice(app.settings.redis_dsn),  # nosec
                    decode_responses=True,
                ).client(),
                prefix=app.name,
            ),
            cache_ttl=app.settings.places_cache_ttl,
        )

        return cast(
            ASGIApplication,
            asgi.SentryAsgiMiddleware(
                bootstrap.create_app(
                    dependencies=bootstrap.create_dependencies(
                        places_repository=places_repository,
                    ),
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
        app=_factory(app),
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
    entrypoint = service.Entrypoint(name="mobile-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
