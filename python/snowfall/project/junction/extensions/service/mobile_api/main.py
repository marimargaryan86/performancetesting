import random
from functools import partial

import aiosmtplib
import httpx
import stripe
from authlib.integrations import httpx_client
from motor import motor_asyncio
from redis import asyncio as aioredis
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
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
from snowfall.service.authentication.v1 import sessions_pb2_grpc
from snowfall.stdlib.format import jwt
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication as starlette_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import client as grpc_transport_client
from snowfall.stdlib.transport.http import auth
from snowfall.vendor.junction import client as base_client
from snowfall.vendor.junction.go import client


def _get_httpx_auth_and_middlewares(
    settings: bootstrap.Settings,
) -> tuple[httpx.Auth, list[Middleware]]:
    httpx_auth_method: httpx.Auth

    if settings.cookie_auth_enabled:
        if not settings.authentication_address or not settings.junction_private_key:
            raise RuntimeError("Missing required configuration.")

        httpx_auth_method = auth.TemporaryTokenAuth()
        custom_middlewares = [
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=starlette_auth.CookieAuthenticationBackend(
                    cookie_to_user=auth_adapter.session_cookie_resolver(
                        session_client=sessions_pb2_grpc.SessionServiceStub(
                            grpc_transport_client.create_channel(
                                settings.authentication_address,
                            ),
                        ),
                    ),
                ),
                on_error=handlers.auth_error_handler,
            ),
            Middleware(
                middleware.HubHackBackend,
                jwt_auth=httpx_auth_method,
                jwt_encoder=jwt.Encoder(
                    private_key=settings.junction_private_key,
                    algorithm="RS256",
                ),
            ),
        ]
    else:
        httpx_auth_method = auth.ClientCredentialsAuth(
            client=httpx_client.AsyncOAuth2Client(
                client_id=settings.ory_client_id,
                client_secret=settings.ory_client_secret,
            ),
            token_endpoint=str(settings.ory_client_token_endpoint),
        )
        custom_middlewares = [
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=middleware.AuthenticationBackend(
                    decoder=jwt.Decoder(
                        public_key=settings.jwt_public_key,
                        algorithms=["RS256"],
                    ),
                    token_version=settings.jwt_token_version,
                ),
                on_error=handlers.auth_error_handler,
            ),
        ]

    return httpx_auth_method, custom_middlewares


async def _http(
    app: application.Application[bootstrap.Settings],
) -> None:
    stripe.api_key = app.settings.stripe_api_key
    httpx_auth, custom_middlewares = _get_httpx_auth_and_middlewares(app.settings)
    junction_httpx_client = base_client.create_httpx_client(
        base_url=app.settings.junction_api_address,
        auth=httpx_auth,
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
        encoder=jwt.Encoder(
            private_key=app.settings.jwt_private_key,
            algorithm="RS256",
        ),
        token_version=app.settings.jwt_token_version,
    )

    with spec.get_api_spec(cookie_auth=app.settings.cookie_auth_enabled) as spec_path:
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
            custom_middlewares=custom_middlewares,
            openapi_path=spec_path,
        )

        asgi_app.add_exception_handler(
            httpx.HTTPStatusError,
            partial(
                mobile_handlers.go_status_error_handler,
                go_urls=[app.settings.junction_api_address],
            ),
        )

        await starlette.serve(
            starlette_app=asgi_app,
            settings=app.settings,
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
            callback=_http,
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
