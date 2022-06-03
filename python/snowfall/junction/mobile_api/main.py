import http
import random
from typing import Callable, cast

import aioredis
import aiosmtplib
import uvicorn
from asgiref.typing import ASGIApplication
from motor import motor_asyncio
from sentry_sdk.integrations import asgi
from starlette.middleware import Middleware, authentication

from snowfall.junction.mobile_api import (
    bootstrap,
    jwt_generator,
    otp_middleware,
    repository,
    smtp,
)
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import handlers, middlewares, validation
from snowfall.stdlib.persistence import filesystem, redis
from snowfall.vendor.junction import client

_SERVICE_NAME = "mobile-api"


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        junction_client = client.JunctionClient(
            api_url=random.choice(app.settings.junction_api_address),  # nosec
            token=app.settings.junction_api_token,
        )
        redis_client = redis.Client[str](
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=True,
            ).client(),
            prefix=app.name,
        )
        mongo = motor_asyncio.AsyncIOMotorClient(
            app.settings.mongo_dsn,  # nosec
        )[_SERVICE_NAME]
        smtp_cl = smtp.EmailClient(
            aiosmtplib.SMTP(
                hostname=app.settings.smtp_dsn.host,
                port=app.settings.smtp_dsn.port,
                username=app.settings.smtp_dsn.user,
                password=app.settings.smtp_dsn.password,
                start_tls=True,
            ),
        )
        jwt_gen = jwt_generator.JwtGenerator(
            jwt_private_key=app.settings.jwt_private_key,
            jwt_token_version=app.settings.jwt_token_version,
        )
        return cast(
            ASGIApplication,
            asgi.SentryAsgiMiddleware(
                bootstrap.create_app(
                    dependencies=bootstrap.create_dependencies(
                        places_repository=repository.PlacesRepository(
                            junction_client=junction_client,
                            redis_client=redis_client,
                            cache_ttl=app.settings.places_cache_ttl,
                        ),
                        users_repository=repository.UsersRepository(
                            mongo["users"],
                        ),
                        otp_repository=repository.OtpRepository(
                            redis_client=redis_client,
                            cache_ttl=app.settings.otp_cache_ttl,
                        ),
                        smtp_client=smtp_cl,
                        orders_repository=repository.OrdersRepository(
                            mongo["orders"],
                        ),
                        junction_client=junction_client,
                        jwt_gen=jwt_gen,
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
                        Middleware(
                            authentication.AuthenticationMiddleware,
                            backend=otp_middleware.OTPAuthenticationBackend(),
                            on_error=handlers.auth_error_handler,
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
