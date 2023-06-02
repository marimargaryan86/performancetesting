from typing import AsyncIterator, Mapping

import httpx
import pytest
from starlette import applications
from starlette.middleware import Middleware

from snowfall.project.pay import fixtures
from snowfall.project.pay.adapter.payments import DictClient, GrpcClient
from snowfall.project.pay.service.webhooks import bootstrap, routers
from snowfall.project.pay.service.webhooks.middlewares import HmacHeaderMiddleware
from snowfall.stdlib.integration.starlette import application


@pytest.fixture()
def secret_key() -> str:
    return "Very-Secret-Key"


@pytest.fixture()
def payment_client() -> DictClient:
    return DictClient(
        fixtures.get_payments(),
    )


@pytest.fixture()
def payment_id() -> str:
    return fixtures.PAYMENTS[0]


@pytest.fixture()
async def external_reference_id(payment_client: DictClient, payment_id: str) -> str:
    return (await payment_client.get(payment_id)).external_reference_id


@pytest.fixture()
def headers() -> dict[str, str]:
    return {}


@pytest.fixture()
def webhook_app(
    payment_client: GrpcClient,
    secret_key: str,
) -> applications.Starlette:
    return create_webhook_app(
        payment_client=payment_client,
        secret_key=secret_key,
    )


def create_webhook_app(
    payment_client: GrpcClient,
    secret_key: str,
) -> applications.Starlette:
    return application.create_starlette_app(
        custom_middlewares=[
            Middleware(HmacHeaderMiddleware, secret_key=secret_key),
        ],
        routes=routers.get_routes(
            bootstrap.create_dependencies(
                payment_client=payment_client,
            ),
        ),
        openapi_path=None,
    )


@pytest.fixture()
async def webhook_client(
    webhook_app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        app=webhook_app,
        base_url="https://example.com",
    ) as client:
        client.headers.update(headers)

        yield client
