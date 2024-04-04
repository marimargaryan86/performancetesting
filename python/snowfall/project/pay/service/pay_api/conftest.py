from __future__ import annotations

import datetime
import pathlib
from collections.abc import AsyncIterator, Mapping, Sequence

import httpx
import pytest
from redis import asyncio as aioredis
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth
from snowfall.adapter.authentication import JWTFactory
from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay import fixtures
from snowfall.project.pay.adapter import (
    companies,
    currencies,
    quotations,
    transactions,
)
from snowfall.project.pay.service.pay_api import authenticator, bootstrap
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.routes import router
from snowfall.project.pay.service.transactions.v1.models_pb2 import (
    Quotation,
    QuotationAmounts,
    QuotationRates,
)
from snowfall.service.authentication.v1.models_pb2 import User
from snowfall.stdlib import money, string
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.persistence.redis import types as redis


async def mock_jwt_to_user_id(token: str) -> str:
    return authenticator.LegacyAuth(jwt.Decoder()).get_user_id_from_jwt(token)


@pytest.fixture()
def custom_middlewares() -> Sequence[Middleware]:
    return [
        Middleware(
            authentication.AuthenticationMiddleware,
            backend=stdlib_auth.JWTAuthenticationBackend(
                jwt_to_user_id=mock_jwt_to_user_id,
            ),
            on_error=handlers.auth_error_handler,
        ),
    ]


def _create_app(
    quotations_client: quotations.Client,
    redis_repository: UserSessionRepository,
    currencies_client: currencies.Client,
    companies_client: companies.Client,
    transactions_client: transactions.Client,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    app = application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes=router.get_routes(
            bootstrap.create_dependencies(
                redis_repository,
                quotations_client,
                companies_client=companies_client,
                currencies_client=currencies_client,
                transactions_client=transactions_client,
            ),
        ),
    )
    app.add_exception_handler(cursor.CursorError, handlers.cursor_error_handler)
    app.add_exception_handler(errors.NotFoundError, handlers.not_found_error_handler)

    return app


def _create_admin_app(
    authentication_client: auth.Client,
    transactions_client: transactions.Client,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    app = application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes=router.get_admin_routes(
            bootstrap.create_admin_dependencies(
                authentication_client,
                transactions_client=transactions_client,
            ),
        ),
    )
    app.add_exception_handler(cursor.CursorError, handlers.cursor_error_handler)
    app.add_exception_handler(errors.NotFoundError, handlers.not_found_error_handler)

    return app


@pytest.fixture()
def redis_client(decoding_redis_client: aioredis.Redis[str]) -> redis.Client[str]:
    return redis.Client(
        decoding_redis_client,
        prefix="pay_api",
    )


@pytest.fixture()
async def redis_repository(
    redis_client: redis.Client[str],
) -> UserSessionRepository:
    return UserSessionRepository(
        redis_client,
        datetime.timedelta(minutes=15),  # noqa: WPS432
    )


@pytest.fixture()
def cc_login() -> str:
    return "cc_login"


@pytest.fixture()
def cc_api_key() -> str:
    return "random_key"


@pytest.fixture()
def transactions_client(
    transaction_ids: Sequence[str],
) -> transactions.Client:
    return transactions.DictClient([])


@pytest.fixture()
def companies_client() -> companies.DictClient:
    return companies.DictClient(fixtures.get_companies())


@pytest.fixture()
def quotations_client(
    quotations_ids: Sequence[str],
) -> quotations.Client:
    return quotations.DictClient(
        [get_quotation(quotations_id) for quotations_id in quotations_ids],
    )


def get_quotation(quotation_id: str) -> Quotation:
    money_usd = money.from_string("1000", money.Currency("USD")).protobuf()
    basic_rate = float(1)
    return Quotation(
        id=quotation_id,
        amounts=QuotationAmounts(
            beneficiary=money_usd,
            base_converted=money_usd,
            fx_margin=money_usd,
            processing_margin=money_usd,
            sales_margin=money_usd,
            quotation=money_usd,
        ),
        rates=QuotationRates(
            fx_quote=basic_rate,
            fx_buffer=basic_rate,
            fx_markup=basic_rate,
            sales_markup=basic_rate,
            processing_markup=basic_rate,
        ),
        payer_id=string.uuid(),
        beneficiary_id=string.uuid(),
    )


@pytest.fixture()
def authentication_client() -> auth.DictClient:
    return auth.DictClient()


@pytest.fixture()
def jwt_token() -> str:
    return jwt.Encoder().encode(
        JWTFactory(
            ttl=datetime.timedelta(hours=1),
        ).from_user(User(email="example@example.com", id=string.uuid())),
    )


@pytest.fixture()
def headers(jwt_token: str) -> dict[str, str]:
    return {
        "Content-Type": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(jwt_token),
    }


@pytest.fixture()
def app(
    quotations_client: quotations.Client,
    redis_repository: UserSessionRepository,
    currencies_client: currencies.Client,
    companies_client: companies.Client,
    transactions_client: transactions.Client,
) -> applications.Starlette:
    return _create_app(
        quotations_client=quotations_client,
        redis_repository=redis_repository,
        currencies_client=currencies_client,
        companies_client=companies_client,
        transactions_client=transactions_client,
        openapi_path=filesystem.resource_path("junction.pay_api", "openapi.json"),
    )


@pytest.fixture()
def admin_app(
    authentication_client: auth.Client,
    transactions_client: transactions.Client,
    custom_middlewares: Sequence[Middleware],
) -> applications.Starlette:
    return _create_admin_app(
        authentication_client=authentication_client,
        transactions_client=transactions_client,
        custom_middlewares=custom_middlewares,
        openapi_path=filesystem.resource_path("junction.pay_admin_api", "openapi.json"),
    )


@pytest.fixture()
async def client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),  # type: ignore[arg-type]
        base_url="https://example.com",
    ) as client:
        client.headers.update(dict(headers))

        yield client


@pytest.fixture()
async def admin_client(
    admin_app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        app=admin_app,
        base_url="https://example.com",
    ) as client:
        client.headers.update(dict(headers))

        yield client
