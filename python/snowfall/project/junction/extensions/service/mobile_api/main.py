import random
from functools import partial
from typing import cast

import aiosmtplib
import httpx
import stripe
from authlib.integrations import httpx_client
from motor import motor_asyncio
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.extensions.service.mobile_api import (
    bootstrap,
    jwt_generator,
    middleware,
    orders_report,
    places_migration,
    repository,
    smtp,
    spec,
)
from snowfall.project.junction.extensions.service.mobile_api import (
    handlers as mobile_handlers,
)
from snowfall.project.junction.extensions.service.mobile_api import (
    plus_client as plus_poc_client,
)
from snowfall.project.junction.extensions.service.mobile_api.routes import router
from snowfall.project.junction.plus.adapter import co2_emissions, flight_delay_predictor
from snowfall.project.junction.plus.service.external_dependencies.v1.grpc_pb2_grpc import (
    CO2EmissionsServiceStub,
)
from snowfall.project.junction.plus.service.flight_prediction.v1 import (
    flight_prediction_pb2_grpc,
)
from snowfall.project.pay.adapter import bills
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.service.authentication.v1 import sessions_pb2_grpc
from snowfall.stdlib.format import jwt
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication as starlette_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.service import application, grpc_factory, redis_factory
from snowfall.stdlib.transport.http import auth
from snowfall.vendor.junction import client as base_client
from snowfall.vendor.junction.go import client as go_client
from snowfall.vendor.junction.plus import client as plus_client


async def _get_httpx_auth_and_middlewares(
    app: application.Application[bootstrap.Settings],
) -> tuple[httpx.Auth, list[Middleware]]:
    httpx_auth_method: httpx.Auth

    if app.settings.cookie_auth_enabled:
        is_configured = (
            app.settings.authentication_address and app.settings.junction_private_key
        )
        if not is_configured:
            raise RuntimeError("Missing required configuration.")

        httpx_auth_method = auth.TemporaryTokenAuth()
        custom_middlewares = [
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=starlette_auth.CookieAuthenticationBackend(
                    cookie_to_user=auth_adapter.session_cookie_resolver(
                        session_client=sessions_pb2_grpc.SessionServiceStub(
                            await grpc_factory.make_insecure_channel(
                                app,
                                cast(str, app.settings.authentication_address),
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
                    private_key=app.settings.junction_private_key,
                    algorithm="RS256",
                ),
            ),
        ]
    else:
        httpx_auth_method = auth.ClientCredentialsAuth(
            client=httpx_client.AsyncOAuth2Client(
                client_id=app.settings.ory_client_id,
                client_secret=app.settings.ory_client_secret,
            ),
            token_endpoint=str(app.settings.ory_client_token_endpoint),
        )
        custom_middlewares = [
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=middleware.AuthenticationBackend(
                    decoder=jwt.Decoder(
                        public_key=app.settings.jwt_public_key,
                        algorithms=["RS256"],
                    ),
                    token_version=app.settings.jwt_token_version,
                ),
                on_error=handlers.auth_error_handler,
            ),
        ]

    return httpx_auth_method, custom_middlewares


async def _http(  # noqa: WPS217
    app: application.Application[bootstrap.Settings],
) -> None:
    stripe.api_key = app.settings.stripe_api_key
    httpx_auth, custom_middlewares = await _get_httpx_auth_and_middlewares(app)
    junction_httpx_client = base_client.create_httpx_client(
        base_url=app.settings.junction_api_address,
        auth=httpx_auth,
        client=httpx.AsyncClient(timeout=10),
    )
    metrics.register(junction_httpx_client)
    junction_client = go_client.Client(
        base_url=app.settings.junction_api_address,
        client=junction_httpx_client,
    )
    plus_http_client = plus_client.Client(
        base_url=app.settings.plus_api_address,
        client=metrics.register(
            base_client.create_httpx_client(
                base_url=app.settings.plus_api_address,
                auth=httpx_auth,
                client=httpx.AsyncClient(timeout=10),
            ),
        ),
    )
    plus_poc_http_client = plus_poc_client.PlusClient(
        api_url=app.settings.plus_poc_api_address,
        activated=app.settings.plus_poc_activated,
        client=metrics.register(httpx.AsyncClient()),
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=True,
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
    transactions_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.transactions_address,
    )
    flight_prediction_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.flight_prediction_address,
    )
    predictions_client = flight_delay_predictor.GrpcClient(
        flight_prediction_pb2_grpc.FlightPredictionServiceStub(
            flight_prediction_channel,
        ),
    )
    co2_emissions_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.co2_emissions_address,
    )
    co2_emissions_client = co2_emissions.GrpcClient(
        CO2EmissionsServiceStub(
            co2_emissions_channel,
        ),
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
                    bills_client=bills.GrpcClient(
                        transactions_pb2_grpc.BillsServiceStub(
                            transactions_channel,
                        ),
                    ),
                    junction_client=junction_client,
                    plus_client=plus_http_client,
                    plus_poc_client=plus_poc_http_client,
                    jwt_gen=jwt_gen,
                    httpx_client=junction_httpx_client,
                    predictions_client=predictions_client,
                    co2_emissions_client=co2_emissions_client,
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
