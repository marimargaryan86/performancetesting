from collections.abc import AsyncIterator

import httpx
import pytest
from starlette import applications
from starlette.middleware import Middleware

from snowfall.project.junction.plus.service.plus_webhooks import (
    bootstrap,
    middlewares,
)
from snowfall.project.junction.plus.service.plus_webhooks.routes import router
from snowfall.stdlib.integration.starlette import application


@pytest.fixture()
def secret_key() -> str:
    return "Very-Secret-Key"


@pytest.fixture()
def cirium_flex_alert_key() -> str:
    return "MQ|3424|ORD|CLE|ARRIVAL_DELAY|2020-04-07T16:16:39.388Z"


@pytest.fixture()
def cirium_flex_alert_hash(cirium_flex_alert_key: str, secret_key: str) -> str:
    return middlewares.calculate_hash(
        cirium_flex_alert_key.encode(),
        secret_key.encode(),
    )


@pytest.fixture()
def app(secret_key: str) -> applications.Starlette:
    return application.create_starlette_app(
        custom_middlewares=[
            Middleware(
                middlewares.HmacHeaderMiddleware,
                secret_key=secret_key,
            ),
        ],
        routes=router.get_routes(
            bootstrap.create_dependencies(),
        ),
        openapi_path=None,
    )


@pytest.fixture()
async def client(
    app: applications.Starlette,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        yield client
