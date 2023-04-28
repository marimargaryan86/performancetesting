import datetime
import random
from typing import Callable

from motor import motor_asyncio
from redis import asyncio as aioredis
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth
from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.adapter import accounts as accounts_adapter
from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.accounts import repositories
from snowfall.project.pay.service.accounts.v1alpha.accounts_pb2_grpc import (
    AccountsServiceStub,
)
from snowfall.project.pay.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.project.pay.service.pay_api import authenticator, bootstrap
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    CompanyRepository,
    ConversionRepository,
    CurrencyRepository,
    TransactionRepository,
)
from snowfall.project.pay.service.pay_api.routes import router
from snowfall.project.pay.service.quotations.quotations import QuotationsRepository
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.grpc.client import create_channel
from snowfall.vendor.currency_cloud.client import CurrencyCloudConfig


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        mongo = motor_asyncio.AsyncIOMotorClient(
            random.choice(app.settings.mongo_dsn),  # nosec
        )
        cc_config = CurrencyCloudConfig(
            app.settings.cc_login,
            app.settings.cc_api_key,
            app.settings.cc_env,
        )
        redis_client = redis.Client[str](
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=True,
            ).client(),
            prefix=app.name,
        )

        orders_channel = create_channel(
            random.choice(app.settings.currencies_address),  # nosec
        )
        quotations_repo = QuotationsRepository(mongo.quotations.quotations)
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
                    cc_config=cc_config,
                    currencies_client=currencies.GrpcClient(
                        currencies_pb2_grpc.CurrencyServiceStub(orders_channel),
                    ),
                    quotations_repository=quotations_repo,
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
                    currencies_repository=CurrencyRepository(
                        app.settings.currencies,
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
            random.choice(app.settings.mongo_dsn),  # nosec
        )
        cc_config = CurrencyCloudConfig(
            app.settings.cc_login,
            app.settings.cc_api_key,
            app.settings.cc_env,
        )
        authentication_channel = create_channel(
            app.settings.authentication_address,
        )
        accounts_channel = create_channel(
            app.settings.accounts_address,
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
                    cc_config=cc_config,
                    authentication_client=auth.GrpcClient(
                        auth.auth_pb2_grpc.AuthenticationServiceStub(
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
                    transactions_repository=TransactionRepository(
                        mongo.transactions.transactions,
                    ),
                    currencies_repository=CurrencyRepository(
                        app.settings.currencies,
                    ),
                    beneficiaries_repository=BeneficiaryRepository(
                        mongo.beneficiaries.beneficiaries,
                    ),
                    accounts_client=accounts_adapter.GrpcClient(
                        AccountsServiceStub(
                            accounts_channel,
                        ),
                    ),
                ),
            ),
            openapi_path=filesystem.resource_path(
                "junction.pay_admin_api",
                "openapi.json",
            ),
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
