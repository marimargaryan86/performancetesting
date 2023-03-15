import base64
import random
from functools import partial
from typing import Callable

import aiosmtplib
import httpx
import stripe
from motor import motor_asyncio
from redis import asyncio as aioredis
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.project.junction.extensions.service.mobile_api import bootstrap
from snowfall.project.junction.extensions.service.mobile_api import (
    currencies as mobile_currencies,
)
from snowfall.project.junction.extensions.service.mobile_api import (
    handlers as mobile_handlers,
)
from snowfall.project.junction.extensions.service.mobile_api import (
    jwt_generator,
    middleware,
    orders_report,
    places_migration,
    repository,
    smtp,
)
from snowfall.project.junction.extensions.service.mobile_api.routes import router
from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.grpc.client import create_channel
from snowfall.vendor.junction import client


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        currencies_channel = create_channel(
            random.choice(app.settings.currencies_address),  # nosec
        )
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
        )[app.settings.mongo_db]
        smtp_cl = smtp.EmailClient(
            aiosmtplib.SMTP(
                hostname=app.settings.smtp_dsn.host,
                port=int(app.settings.smtp_dsn.port or 0) or None,
                username=app.settings.smtp_dsn.user,
                password=app.settings.smtp_dsn.password,
                start_tls=True,
            ),
            client_name=app.settings.client_name,
            support_email=app.settings.support_email,
        )
        jwt_gen = jwt_generator.JwtGenerator(
            jwt_private_key=app.settings.jwt_private_key,
            jwt_token_version=app.settings.jwt_token_version,
        )

        asgi_app = application.create_starlette_app(
            routes=router.get_routes(
                bootstrap.create_dependencies(
                    currencies_client=mobile_currencies.CurrencyClient(
                        app.settings.currency_rate_cache_ttl,
                        currencies.GrpcClient(
                            currencies_pb2_grpc.CurrencyServiceStub(currencies_channel),
                        ),
                        fallback_rates={"SEK": app.settings.fallback_rate_sek},
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
                    offers_rates_repository=repository.OffersRatesRepository(
                        redis_client=redis_client,
                        cache_ttl=app.settings.offers_rates_cache_ttl,
                    ),
                    enums_values_repository=repository.EnumsValuesRepository(
                        redis_client=redis_client,
                    ),
                    stripe_users_repository=repository.StripeUsersRepository(
                        mongo["stripe_users"],
                        create_stripe_customers=app.settings.create_stripe_customers,
                    ),
                    smtp_client=smtp_cl,
                    orders_repository=repository.OrdersRepository(
                        mongo["orders"],
                    ),
                    preferences_repository=repository.PreferencesRepository(
                        mongo["preferences"],
                    ),
                    loyalty_programs_repository=repository.LoyaltyProgramsRepository(
                        mongo["air_loyalty"],
                    ),
                    vouchers_repository=repository.VouchersRepository(
                        mongo["vouchers"],
                    ),
                    notification_tokens_repository=repository.NotificationTokensRepository(
                        mongo["notifications"],
                    ),
                    user_groups_repository=repository.UserGroupsRepository(
                        mongo["user_groups"],
                    ),
                    junction_client=junction_client,
                    jwt_gen=jwt_gen,
                ),
            ),
            custom_middlewares=[
                Middleware(
                    authentication.AuthenticationMiddleware,
                    backend=middleware.AuthenticationBackend(
                        token_version=app.settings.jwt_token_version,
                        public_key=base64.b64decode(
                            app.settings.jwt_public_key.encode(),
                        ).decode(),
                    ),
                    on_error=handlers.auth_error_handler,
                ),
            ],
            openapi_path=filesystem.resource_path(
                "junction/mobile_api",
                "openapi.json",
            ),
            validate_response=app.settings.validate_responses_against_spec,
        )
        asgi_app.add_exception_handler(
            httpx.HTTPStatusError,
            partial(
                mobile_handlers.go_status_error_handler,
                go_urls=app.settings.junction_api_address,
            ),
        )
        return asgi_app

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


async def _orders_report(app: service.Application[orders_report.Settings]) -> None:
    await orders_report.orders_report(app)


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
        service.Command(
            name="orders_report",
            callback=_orders_report,
            settings_class=orders_report.Settings,
        ),
    )
