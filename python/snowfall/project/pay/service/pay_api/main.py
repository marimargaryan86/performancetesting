import datetime
import random
from collections.abc import AsyncGenerator, Callable
from typing import Any

from motor import motor_asyncio
from redis import asyncio as aioredis
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth
from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.adapter import accounts as accounts_adapter
from snowfall.project.pay.adapter import companies as companies_adapter
from snowfall.project.pay.adapter import (
    conversions,
    currencies,
    payments,
    quotations,
    transactions,
)
from snowfall.project.pay.service.companies import repositories
from snowfall.project.pay.service.companies.v1alpha.grpc_pb2_grpc import (
    AccountsServiceStub,
    CompaniesServiceStub,
)
from snowfall.project.pay.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.project.pay.service.pay_api import authenticator, bootstrap
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    CompanyRepository,
    ConversionRepository,
    TransactionRepository,
)
from snowfall.project.pay.service.pay_api.routes import router
from snowfall.project.pay.service.payments.v1alpha.payments_pb2_grpc import (
    PaymentsServiceStub,
)
from snowfall.project.pay.service.transactions.v1alpha import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.service.authentication.v1 import authentication_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.grpc.client import create_channel
from snowfall.vendor.currency_cloud.client import CurrencyCloudAuth, PaymentClient


def _lifespan(
    payment_client: PaymentClient,
    redis_client: redis.Client[str],
) -> Callable[[applications.Starlette], AsyncGenerator[Any, Any]]:
    async def decorator(app: applications.Starlette) -> AsyncGenerator[Any, Any]:
        redis_key = "HouseAccount"
        account = await payment_client.get_house_account()
        await redis_client.put(redis_key, account.json(exclude_none=True))
        yield
        await redis_client.delete(redis_key)

    return decorator


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        mongo = motor_asyncio.AsyncIOMotorClient(
            random.choice(app.settings.mongo_dsn),  # noqa: S311
        )
        redis_client = redis.Client[str](
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # noqa: S311
                decode_responses=True,
            ).client(),
            prefix=app.name,
        )

        transactions_channel = create_channel(
            app.settings.transactions_address,
        )
        currencies_channel = create_channel(
            app.settings.currencies_address,
        )
        asgi_app = application.create_starlette_app(
            custom_middlewares=[
                Middleware(
                    authentication.AuthenticationMiddleware,
                    backend=authenticator.Authenticator(
                        public_key_content=app.settings.jwt_public_key,
                    ),
                    on_error=handlers.auth_error_handler,
                ),
            ],
            routes=router.get_routes(
                bootstrap.create_dependencies(
                    payment_client=PaymentClient(
                        base_url=app.settings.cc_address,
                        auth=CurrencyCloudAuth(
                            base_url=app.settings.cc_address,
                            login_id=app.settings.cc_login,
                            api_key=app.settings.cc_api_key,
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
                    transactions_repository=TransactionRepository(
                        mongo.transactions.transactions,
                    ),
                    conversions_repository=ConversionRepository(
                        mongo.conversions.conversions,
                    ),
                    companies_repository=CompanyRepository(
                        mongo.companies.companies,
                    ),
                    transactions_client=transactions.GrpcClient(
                        transactions_pb2_grpc.TransactionsServiceStub(
                            transactions_channel,
                        ),
                    ),
                    quotations_client=quotations.GrpcClient(
                        transactions_pb2_grpc.QuotationsServiceStub(
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

        return asgi_app

    return decorator


def _admin_factory(
    app: service.Application[bootstrap.AdminSettings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        mongo = motor_asyncio.AsyncIOMotorClient(
            random.choice(app.settings.mongo_dsn),  # noqa: S311
        )
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
        currencies_channel = create_channel(
            app.settings.currencies_address,
        )
        cc_payment_client = PaymentClient(
            base_url=app.settings.cc_address,
            auth=CurrencyCloudAuth(
                base_url=app.settings.cc_address,
                login_id=app.settings.cc_login,
                api_key=app.settings.cc_api_key,
            ),
        )
        redis_client = redis.Client[str](
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # noqa: S311
                decode_responses=True,
            ).client(),
            prefix=app.name,
        )
        asgi_app = application.create_starlette_app(
            custom_middlewares=[
                Middleware(
                    authentication.AuthenticationMiddleware,
                    backend=authenticator.Authenticator(
                        public_key_content=app.settings.jwt_public_key,
                    ),
                    on_error=handlers.auth_error_handler,
                ),
            ],
            routes=router.get_admin_routes(
                bootstrap.create_admin_dependencies(
                    cc_payment_client=cc_payment_client,
                    authentication_client=auth.GrpcClient(
                        authentication_pb2_grpc.AuthenticationServiceStub(
                            authentication_channel,
                        ),
                    ),
                    companies_repository=CompanyRepository(
                        mongo.companies.companies,
                    ),
                    contacts_repository=repositories.ContactsRepository(
                        mongo.contacts.contacts,
                    ),
                    conversions_repository=ConversionRepository(
                        mongo.conversions.conversions,
                    ),
                    beneficiaries_repository=BeneficiaryRepository(
                        mongo.beneficiaries.beneficiaries,
                    ),
                    accounts_client=accounts_adapter.GrpcClient(
                        AccountsServiceStub(
                            companies_channel,
                        ),
                    ),
                    companies_client=companies_adapter.GrpcClient(
                        CompaniesServiceStub(
                            companies_channel,
                        ),
                    ),
                    transactions_client=transactions.GrpcClient(
                        transactions_pb2_grpc.TransactionsServiceStub(
                            transactions_channel,
                        ),
                    ),
                    conversions_client=conversions.GrpcClient(
                        transactions_pb2_grpc.ConversionsServiceStub(
                            transactions_channel,
                        ),
                    ),
                    currencies_client=currencies.GrpcClient(
                        currencies_pb2_grpc.CurrencyServiceStub(
                            currencies_channel,
                        ),
                    ),
                    transactions_repository=TransactionRepository(
                        mongo.transactions.transactions,
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

        return asgi_app

    return decorator


def _serve(app: service.Application[bootstrap.Settings]) -> None:
    application.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


def _admin_serve(app: service.Application[bootstrap.AdminSettings]) -> None:
    application.serve(
        factory=_admin_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="pay-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
        service.Command(
            name="admin-http",
            callback=_admin_serve,
            settings_class=bootstrap.AdminSettings,
        ),
    )
