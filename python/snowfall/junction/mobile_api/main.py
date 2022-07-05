import base64
import random
from typing import Callable

import aioredis
import aiosmtplib
import stripe
from asgiref.typing import ASGIApplication
from motor import motor_asyncio
from starlette.middleware import Middleware, authentication

from snowfall.junction.mobile_api import (
    auth_middleware,
    bootstrap,
    jwt_generator,
    places_migration,
    repository,
    smtp,
)
from snowfall.junction.mobile_api.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.junction import client


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], ASGIApplication]:
    def decorator() -> ASGIApplication:
        stripe.api_key = app.settings.stripe_api_key
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
        )[app.name]
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

        return application.create_asgi_app(
            routes_factory=router.get_routes,
            dependencies=bootstrap.create_dependencies(
                offers_repository=repository.OffersRepository(
                    mongo["offers"],
                ),
                places_repository=repository.PlacesRepository(
                    mongo["places"],
                ),
                users_repository=repository.UsersRepository(
                    mongo["users"],
                ),
                otp_repository=repository.OtpRepository(
                    redis_client=redis_client,
                    cache_ttl=app.settings.otp_cache_ttl,
                ),
                stripe_users_repository=repository.StripeUsersRepository(
                    mongo["stripe_users"],
                ),
                smtp_client=smtp_cl,
                orders_repository=repository.OrdersRepository(
                    mongo["orders"],
                ),
                trip_searches_repository=repository.TripSearchesRepository(
                    mongo["trip-searches"],
                ),
                trips_repository=repository.TripsRepository(mongo["trips"]),
                junction_client=junction_client,
                jwt_gen=jwt_gen,
            ),
            custom_middlewares=[
                Middleware(
                    authentication.AuthenticationMiddleware,
                    backend=auth_middleware.AuthenticationBackend(
                        token_version=app.settings.jwt_token_version,
                        public_key=base64.b64decode(
                            app.settings.jwt_public_key.encode(),
                        ).decode(),
                    ),
                    on_error=handlers.auth_error_handler,
                ),
            ],
            openapi_path=filesystem.resource_path("mobile_api", "openapi.json"),
        )

    return decorator


def _serve(app: service.Application[bootstrap.Settings]) -> None:
    application.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


async def _migrate(app: service.Application[bootstrap.Settings]) -> None:
    await places_migration.migrate(app.settings)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="mobile-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
        service.Command(
            name="migrate",
            callback=_migrate,
            settings_class=bootstrap.Settings,
        ),
    )
