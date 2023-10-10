import datetime
from collections.abc import AsyncGenerator, Callable
from typing import Any

import httpx
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth_adapter
from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.adapter import (
    beneficiaries,
    companies,
    currencies,
    payments,
    quotations,
    transactions,
)
from snowfall.project.pay.service.companies.v1alpha import (
    grpc_pb2_grpc as companies_grpc_pb2,
)
from snowfall.project.pay.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.project.pay.service.pay_api import authenticator, bootstrap
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.routes import router
from snowfall.project.pay.service.payments.v1alpha.payments_pb2_grpc import (
    PaymentsServiceStub,
)
from snowfall.project.pay.service.transactions.v1alpha import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.service.authentication.v1 import authentication_pb2_grpc, oauth_pb2_grpc
from snowfall.stdlib.format import jwt
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application, redis_factory
from snowfall.stdlib.transport.grpc.client import create_channel
from snowfall.vendor.currency_cloud import client


def _lifespan(
    payment_client: client.PaymentClient,
    redis_client: redis.Client[str],
) -> Callable[[applications.Starlette], AsyncGenerator[Any, Any]]:
    async def decorator(app: applications.Starlette) -> AsyncGenerator[Any, Any]:
        redis_key = "HouseAccount"
        account = await payment_client.get_house_account()
        await redis_client.put(redis_key, account.json(exclude_none=True))
        yield
        await redis_client.delete(redis_key)

    return decorator


async def _http(
    app: application.Application[bootstrap.Settings],
) -> None:
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=True,
    )
    authentication_channel = create_channel(
        app.settings.authentication_address,
    )
    transactions_channel = create_channel(
        app.settings.transactions_address,
    )
    currencies_channel = create_channel(
        app.settings.currencies_address,
    )
    companies_channel = create_channel(
        app.settings.companies_address,
    )
    asgi_app = starlette.create_starlette_app(
        custom_middlewares=[
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=stdlib_auth.JWTAuthenticationBackend(
                    stdlib_auth.OryAuth(
                        jwk_client=jwt.AsyncJWKClient(
                            jwk_url=auth_adapter.get_jwk_url(
                                app.settings.authentication_address,
                            ),
                            key_ttl=app.settings.ory_jwk_ttl,
                        ),
                        legacy_fallback=authenticator.LegacyAuth(
                            decoder=jwt.Decoder(
                                public_key=app.settings.jwt_public_key,
                                algorithms=["RS256"],
                            ),
                        ).get_user_id_from_jwt,
                        client_resolver=auth_adapter.oauth_client_resolver(
                            oauth_client=oauth_pb2_grpc.OAuthServiceStub(
                                authentication_channel,
                            ),
                        ),
                    ).get_owner_from_jwt,
                ),
                on_error=handlers.auth_error_handler,
            ),
        ],
        routes=router.get_routes(
            bootstrap.create_dependencies(
                quotations_client=quotations.GrpcClient(
                    transactions_pb2_grpc.QuotationsServiceStub(
                        transactions_channel,
                    ),
                ),
                currencies_client=currencies.GrpcClient(
                    currencies_pb2_grpc.CurrencyServiceStub(
                        currencies_channel,
                    ),
                ),
                redis_client=UserSessionRepository(
                    redis_client=redis_client,
                    cache_ttl=datetime.timedelta(minutes=15),
                ),
                companies_client=companies.GrpcClient(
                    companies_grpc_pb2.CompaniesServiceStub(
                        companies_channel,
                    ),
                ),
                transactions_client=transactions.GrpcClient(
                    transactions_pb2_grpc.TransactionsServiceStub(
                        transactions_channel,
                    ),
                ),
            ),
        ),
        openapi_path=filesystem.resource_path("junction.pay_api", "openapi.json"),
    )

    asgi_app.add_exception_handler(
        cursor.CursorError,
        handlers.cursor_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.ServiceUnavailableError,
        handlers.service_unavailable_error_handler,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


async def _admin_http(
    app: application.Application[bootstrap.AdminSettings],
) -> None:
    authentication_channel = create_channel(
        app.settings.authentication_address,
    )
    companies_channel = create_channel(
        app.settings.companies_address,
    )
    payments_channel = create_channel(
        app.settings.payments_address,
    )
    transactions_channel = create_channel(
        app.settings.transactions_address,
    )
    cc_payment_client = client.PaymentClient(
        base_url=app.settings.cc_address,
        auth=client.CurrencyCloudAuth(
            base_url=app.settings.cc_address,
            login_id=app.settings.cc_login,
            api_key=app.settings.cc_api_key,
        ),
        client=metrics.register(httpx.AsyncClient()),
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=True,
    )
    asgi_app = starlette.create_starlette_app(
        custom_middlewares=[
            Middleware(
                authentication.AuthenticationMiddleware,
                backend=stdlib_auth.JWTAuthenticationBackend(
                    stdlib_auth.OryAuth(
                        jwk_client=jwt.AsyncJWKClient(
                            jwk_url=auth_adapter.get_jwk_url(
                                app.settings.authentication_address,
                            ),
                            key_ttl=app.settings.ory_jwk_ttl,
                        ),
                        legacy_fallback=authenticator.LegacyAuth(
                            decoder=jwt.Decoder(
                                public_key=app.settings.jwt_public_key,
                                algorithms=["RS256"],
                            ),
                        ).get_user_id_from_jwt,
                        client_resolver=auth_adapter.oauth_client_resolver(
                            oauth_client=oauth_pb2_grpc.OAuthServiceStub(
                                authentication_channel,
                            ),
                        ),
                    ).get_owner_from_jwt,
                ),
                on_error=handlers.auth_error_handler,
            ),
        ],
        routes=router.get_admin_routes(
            bootstrap.create_admin_dependencies(
                authentication_client=auth_adapter.GrpcClient(
                    authentication_pb2_grpc.AuthenticationServiceStub(
                        authentication_channel,
                    ),
                ),
                beneficiaries_client=beneficiaries.GrpcClient(
                    companies_grpc_pb2.BeneficiariesServiceStub(
                        companies_channel,
                    ),
                ),
                transactions_client=transactions.GrpcClient(
                    transactions_pb2_grpc.TransactionsServiceStub(
                        transactions_channel,
                    ),
                ),
                payments_client=payments.GrpcClient(
                    PaymentsServiceStub(
                        payments_channel,
                    ),
                ),
            ),
        ),
        openapi_path=filesystem.resource_path(
            "junction.pay_admin_api",
            "openapi.json",
        ),
        lifespan=_lifespan(cc_payment_client, redis_client),
    )

    asgi_app.add_exception_handler(
        cursor.CursorError,
        handlers.cursor_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.ServiceUnavailableError,
        handlers.service_unavailable_error_handler,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="pay-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
        application.Command(
            name="admin-http",
            callback=_admin_http,
            settings_class=bootstrap.AdminSettings,
        ),
    )
