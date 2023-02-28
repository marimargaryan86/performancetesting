import base64
import datetime
import random
from typing import Callable

import currencycloud
from motor import motor_asyncio
from redis import asyncio as aioredis
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.project.adapter import authentication as auth
from snowfall.project.junction.adapter import errors
from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.accounts import accounts
from snowfall.project.pay.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.project.pay.service.pay_api import authenticator, bootstrap
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.repositories import (
    CompanyRepository,
    ConversionRepository,
    TransactionRepository,
)
from snowfall.project.pay.service.pay_api.routes import router
from snowfall.project.pay.service.quotations.quotations import QuotationsRepository
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        mongo = motor_asyncio.AsyncIOMotorClient(
            random.choice(app.settings.mongo_dsn),  # nosec
        )
        cc_client = currencycloud.Client(
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

        authentication_channel = create_channel(
            app.settings.authentication_address,
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
                        public_key_content=base64.b64decode(
                            app.settings.jwt_public_key.encode(),
                        ).decode(),
                    ),
                    on_error=handlers.auth_error_handler,
                ),
            ],
            routes=router.get_routes(
                bootstrap.create_dependencies(
                    cc_client=cc_client,
                    currencies_client=currencies.GrpcClient(
                        currencies_pb2_grpc.CurrencyServiceStub(orders_channel),
                    ),
                    authentication_client=auth.GrpcClient(
                        auth.auth_pb2_grpc.AuthenticationServiceStub(
                            authentication_channel,
                        ),
                    ),
                    quotations_repository=quotations_repo,
                    redis_client=UserSessionRepository(
                        redis_client=redis_client,
                        cache_ttl=datetime.timedelta(minutes=15),
                    ),
                    companies_repository=CompanyRepository(
                        mongo.companies.companies,
                    ),
                    transactions_repository=TransactionRepository(
                        mongo.transactions.transactions,
                    ),
                    conversions_repository=ConversionRepository(
                        mongo.conversions.conversions,
                    ),
                    contact_persons_repository=accounts.ContactPersonsRepository(
                        mongo.contactpersons.contactpersons,
                    ),
                    accounts_repository=accounts.AccountsRepository(
                        mongo.accounts.accounts,
                    ),
                ),
            ),
            openapi_path=filesystem.resource_path("junction.pay_api", "openapi.json"),
        )

        asgi_app.add_exception_handler(
            errors.CursorError,
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
    app: service.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        mongo = motor_asyncio.AsyncIOMotorClient(
            random.choice(app.settings.mongo_dsn),  # nosec
        )
        cc_client = currencycloud.Client(
            app.settings.cc_login,
            app.settings.cc_api_key,
            app.settings.cc_env,
        )
        authentication_channel = create_channel(
            app.settings.authentication_address,
        )
        asgi_app = application.create_starlette_app(
            custom_middlewares=[
                Middleware(
                    authentication.AuthenticationMiddleware,
                    backend=authenticator.Authenticator(
                        public_key_content=base64.b64decode(
                            app.settings.jwt_public_key.encode(),
                        ).decode(),
                    ),
                    on_error=handlers.auth_error_handler,
                ),
            ],
            routes=router.get_admin_routes(
                bootstrap.create_admin_dependencies(
                    cc_client=cc_client,
                    authentication_client=auth.GrpcClient(
                        auth.auth_pb2_grpc.AuthenticationServiceStub(
                            authentication_channel,
                        ),
                    ),
                    companies_repository=CompanyRepository(
                        mongo.companies.companies,
                    ),
                    contact_persons_repository=accounts.ContactPersonsRepository(
                        mongo.contactpersons.contactpersons,
                    ),
                ),
            ),
            openapi_path=filesystem.resource_path(
                "junction.pay_admin_api",
                "openapi.json",
            ),
        )

        asgi_app.add_exception_handler(
            errors.CursorError,
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


def _admin_serve(app: service.Application[bootstrap.Settings]) -> None:
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
            settings_class=bootstrap.Settings,
        ),
    )
