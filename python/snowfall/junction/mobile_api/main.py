import http
import random
from typing import Callable, cast

import aioredis
import uvicorn
from asgiref.typing import ASGIApplication
from motor import motor_asyncio
from sentry_sdk.integrations import asgi
from starlette.middleware import Middleware

from snowfall.junction.mobile_api import bootstrap, repository
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import middlewares, validation
from snowfall.stdlib.persistence import filesystem, redis
from snowfall.vendor.junction import client

_SERVICE_NAME = "mobile-api"
_ORDERS_COLLECTION = "orders"


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        junction_client = client.JunctionClient(
            api_url=random.choice(app.settings.junction_url),  # nosec
            token=app.settings.junction_token,
        )

        places_repository = repository.PlacesRepository(
            junction_client=junction_client,
            redis_client=redis.Client[str](
                aioredis.from_url(
                    random.choice(app.settings.redis_dsn),  # nosec
                    decode_responses=True,
                ).client(),
                prefix=app.name,
            ),
            cache_ttl=app.settings.places_cache_ttl,
        )

        mongo = motor_asyncio.AsyncIOMotorClient(
            app.settings.mongo_dsn,  # nosec
        )
        return cast(
            ASGIApplication,
            asgi.SentryAsgiMiddleware(
                bootstrap.create_app(
                    dependencies=bootstrap.create_dependencies(
                        places_repository=places_repository,
                        orders_repository=repository.OrdersRepository(
                            mongo[_SERVICE_NAME][_ORDERS_COLLECTION],
                        ),
                        junction_client=junction_client,
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
    entrypoint = service.Entrypoint(name=_SERVICE_NAME)

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
