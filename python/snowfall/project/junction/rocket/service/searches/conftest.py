from __future__ import annotations

import datetime
from unittest import mock

import pytest
from motor import motor_asyncio

from snowfall.project.junction.rocket.service.searches import amqp, grpc, repository
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.grpc import testing


@pytest.fixture()
async def search_result_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> repository.SearchResultRepository:
    return repository.SearchResultRepository(
        collection=mongo_client.test.search_results,
    )


@pytest.fixture()
async def offer_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> repository.OfferRepository:
    return repository.OfferRepository(collection=mongo_client.test.offers)


@pytest.fixture()
async def repository_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> repository.SearchRepository:
    return repository.SearchRepository(
        collection=mongo_client.test.searches,
        ttl=datetime.timedelta(days=1),
    )


@pytest.fixture()
async def quote_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> repository.QuoteRepository:
    return repository.QuoteRepository(
        mongo_client.test.quotes,
        datetime.timedelta(minutes=15),
    )


@pytest.fixture()
def producer_obj() -> mock.AsyncMock:
    return mock.create_autospec(producer.Producer, instance=True, spec_set=True)


@pytest.fixture()
def quote_service_tester(
    quote_repository: repository.QuoteRepository,
    producer_obj: mock.AsyncMock,
) -> testing.ServerTester:
    return testing.ServerTester(
        grpc.QuoteService(
            quotes_repo=quote_repository,
            publisher=amqp.QuoteTaskProducer(
                producer=producer_obj,
                routing_key="quotes.offers",
            ),
        ),
    )
