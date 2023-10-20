from collections.abc import AsyncIterator
from unittest import mock

import httpx
import pytest
from starlette import applications

from snowfall.project.junction.go.service.zendesk_webhook import amqp, bootstrap, router
from snowfall.stdlib.integration.starlette import application


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
        openapi_path=None,
    )
