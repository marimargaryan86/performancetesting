import base64
import pathlib
import random
from collections.abc import Callable
from functools import partial

import aiosmtplib
import httpx
import stripe
from authlib.integrations import httpx_client
from motor import motor_asyncio
from redis import asyncio as aioredis
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.project.junction.extensions.service.mobile_api import (
    bootstrap,
    jwt_generator,
    middleware,
    orders_report,
    places_migration,
    plus_client,
    repository,
    smtp,
    spec,
)
from snowfall.project.junction.extensions.service.mobile_api import (
    handlers as mobile_handlers,
)
from snowfall.project.junction.extensions.service.mobile_api.routes import router
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.http import auth
from snowfall.vendor.junction import client as base_client
from snowfall.vendor.junction.go import client


def _factory(
    app: application.Application[bootstrap.Settings],
    api_spec_path: pathlib.Path,
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        stripe.api_key = app.settings.stripe_api_key
        junction_httpx_client = base_client.create_httpx_client(
            base_url=app.settings.junction_api_address,
            auth=auth.ClientCredentialsAuth(
                client=httpx_client.AsyncOAuth2Client(
                    client_id=app.settings.ory_client_id,
                    client_secret=app.settings.ory_client_secret,
                ),
                token_endpoint=str(app.settings.ory_client_token_endpoint),
            ),
            client=httpx.AsyncClient(timeout=10),
        )
        metrics.register(junction_httpx_client)
        junction_client = client.Client(
            base_url=app.settings.junction_api_address,
            client=junction_httpx_client,
        )
        plus_http_client = plus_client.PlusClient(
            api_url=app.settings.plus_api_address,
            activated=app.settings.plus_activated,
            client=metrics.register(httpx.AsyncClient()),
        )
        redis_client = redis.Client[str](
            aioredis.from_url(
                str(random.choice(app.settings.redis_dsn)),  # noqa: S311
                decode_responses=True,
                retry_on_error=[aioredis.ConnectionError],
            ).client(),
            prefix=app.name,
        )
        mongo = motor_asyncio.AsyncIOMotorClient(
            str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
        )[app.settings.mongo_db]
        smtp_cl = smtp.EmailClient(
            aiosmtplib.SMTP(
                hostname=app.settings.smtp_dsn.host,
                port=int(app.settings.smtp_dsn.port or 0) or None,
                username=app.settings.smtp_dsn.username,
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

        asgi_app = starlette.create_starlette_app(
            routes=router.get_routes(
                bootstrap.create_dependencies(
                    places_repository=repository.PlacesRepository(
                        mongo["places"],
                    ),
                    users_repository=repository.UsersRepository(
                        mongo["users"],
                    ),
                    guests_repository=repository.GuestsRepository(
                        mongo["guests"],
                    ),
                    otp_repository=repository.OtpRepository(
                        redis_client=redis_client,
                        cache_ttl=app.settings.otp_cache_ttl,
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
                    markups_repository=repository.MarkupsRepository(
                        mongo["markups"],
                    ),
                    junction_client=junction_client,
                    plus_http_client=plus_http_client,
                    jwt_gen=jwt_gen,
                    httpx_client=junction_httpx_client,
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
            openapi_path=api_spec_path,
        )

        asgi_app.add_exception_handler(
            httpx.HTTPStatusError,
            partial(
                mobile_handlers.go_status_error_handler,
                go_urls=[app.settings.junction_api_address],
            ),
        )
        return asgi_app

    return decorator


def _serve(app: application.Application[bootstrap.Settings]) -> None:
    with spec.get_api_spec() as temp_spec_path:
        starlette.serve(
            factory=_factory(app, temp_spec_path),
            host=str(app.settings.http_address),
            port=app.settings.http_port,
            allowed_proxy_ips=app.settings.forwarded_allowed_ips,
        )


async def _migrate(app: application.Application[bootstrap.MigrateSettings]) -> None:
    await places_migration.migrate(app.settings)


async def _orders_report(app: application.Application[orders_report.Settings]) -> None:
    await orders_report.orders_report(app)


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="mobile-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
        application.Command(
            name="migrate",
            callback=_migrate,
            settings_class=bootstrap.MigrateSettings,
        ),
        application.Command(
            name="orders_report",
            callback=_orders_report,
            settings_class=orders_report.Settings,
        ),
    )
