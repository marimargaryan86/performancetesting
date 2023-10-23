from collections.abc import AsyncIterator
from unittest import mock

import httpx
import pytest
from starlette import applications, middleware

from snowfall.project.junction.go.service.zendesk_webhook import amqp, bootstrap, router
from snowfall.project.junction.go.service.zendesk_webhook.midleware import (
    ZendeskSignatureValidator,
)
from snowfall.stdlib.integration.starlette import application

WEBHOOK_SIGNING_SECRET = "1B2M2Y8AsgTpgAmY7PhCftQdjNmPALIE6YAJmOz4Qn4="


@pytest.fixture()
async def client(
    app: applications.Starlette,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        yield client


@pytest.fixture()
async def event_producer() -> amqp.EventProducer:
    return mock.create_autospec(amqp.EventProducer)


@pytest.fixture()
def app(
    event_producer: amqp.EventProducer,
) -> applications.Starlette:
    return application.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                event_producer=event_producer,
            ),
        ),
        custom_middlewares=[
            middleware.Middleware(
                ZendeskSignatureValidator,
                secret=WEBHOOK_SIGNING_SECRET,
            ),
        ],
        openapi_path=None,
    )
