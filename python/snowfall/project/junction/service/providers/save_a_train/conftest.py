from __future__ import annotations

import datetime
from collections.abc import AsyncIterator
from typing import Any
from unittest import mock

import aiofiles
import httpx
import orjson
import pytest
from aio_pika import Connection, connection
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.provider import cabin_classes, notifications
from snowfall.project.junction.service.providers.save_a_train import (
    adapter,
    cache,
    consumer,
    train_stations,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.save_a_train import client


async def load_json_fixture(
    file_name: str,
) -> dict[str, Any]:
    file_path = filesystem.resource_path(
        package="snowfall.project.junction.service.providers.save_a_train.conftest",
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    async with aiofiles.open(file_path) as file_handle:
        return orjson.loads(await file_handle.read())


@pytest.fixture()
async def storage() -> AsyncIterator[filesystem.Storage]:
    async with filesystem.Storage.from_dsn("memory://") as storage_obj:
        yield storage_obj


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def save_a_train_client(http_client: httpx.AsyncClient) -> client.SATClient:
    return client.SATClient(
        email="test@snowfall.com",
        password="secret",
        password_search="secret",
        token="token",
        api_url="https://test_url",
        api_search_url="https://test_url/searches",
        api_search_timeout=10,
        api_search_requests_limit=1,
        client=http_client,
    )


@pytest.fixture()
def train_station_repository() -> train_stations.TrainStationRepository:
    return train_stations.TrainStationRepository(
        train_stations=[],
    )


@pytest.fixture()
async def provider_cabin_class_mapping(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> cabin_classes.CabinMappingRepository:
    return cabin_classes.CabinMappingRepository(collection=mongo_client.test.test)


@pytest.fixture()
def save_a_train_adapter(
    save_a_train_client: client.SATClient,
    train_station_repository: train_stations.TrainStationRepository,
    provider_cabin_class_mapping: cabin_classes.CabinMappingRepository,
    redis_client: aioredis.Redis[bytes],
    storage: filesystem.Storage,
) -> adapter.SaveATrainAdapter:
    return adapter.SaveATrainAdapter(
        save_a_train_client=save_a_train_client,
        train_station_repository=train_station_repository,
        provider_cabin_class_mapping=provider_cabin_class_mapping,
        offers_cache=cache.OffersCache(
            client=redis.Client(redis_client),
        ),
        ttl=datetime.timedelta(minutes=1),
        notifier=notifications.LogNotifier(),
        notifications_producer=producer.Producer(
            Connection(connection.make_url("")),
            types.Exchange("notifications"),
        ),
        booking_storage=storage,
    )


@pytest.fixture()
def consumer_obj() -> mock.AsyncMock:
    mock_consumer = mock.create_autospec(amqp_consumer.Consumer)
    return mock_consumer.return_value


@pytest.fixture()
def producer_obj() -> mock.AsyncMock:
    mock_producer = mock.create_autospec(producer.Producer)
    return mock_producer.return_value


@pytest.fixture()
def price_ttl() -> datetime.timedelta:
    return datetime.timedelta(minutes=1)


@pytest.fixture()
def provider_company_id() -> str:
    return "provider_id"


@pytest.fixture()
def offer_cache() -> cache.OffersCache:
    return cache.OffersCache(client=redis.Client(aioredis.Redis()))


@pytest.fixture()
def offer_details() -> cache.OfferDetails:
    return cache.OfferDetails(
        search_id="test_search_id",
        search_result_id=mock.MagicMock(),
        transfer_id=mock.MagicMock(),
        fare_id=mock.MagicMock(),
        price="100.00",
        currency="USD",
    )


@pytest.fixture()
def price_quote_consumer(
    consumer_obj: mock.AsyncMock,
    producer_obj: mock.AsyncMock,
    price_ttl: datetime.timedelta,
    provider_company_id: str,
    redis_client: aioredis.Redis[bytes],
) -> consumer.PriceQuoteConsumer:
    return consumer.PriceQuoteConsumer(
        consumer_obj=consumer_obj,
        producer_obj=producer_obj,
        offer_cache=cache.OffersCache(
            client=redis.Client(redis_client),
        ),
        price_quote_cache=cache.PriceQuoteCache(
            client=redis.Client(redis_client),
        ),
        price_ttl=price_ttl,
        provider_company_id=provider_company_id,
    )


@pytest.fixture()
async def option_id(
    price_quote_consumer: consumer.PriceQuoteConsumer,
    offer_details: cache.OfferDetails,
) -> str:
    return await price_quote_consumer._offer_cache.store(  # noqa: SLF001
        record=offer_details,
    )


@pytest.fixture()
async def message(
    option_id: str,
) -> AsyncIterator[types.Message[offers_amqp_pb2.TripPriceQuoteTask]]:
    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as mock_message:
        message = mock_message.return_value
        message.body = offers_amqp_pb2.TripPriceQuoteTask(
            option_id=option_id,
            reseller_id="reseller_id",
            session_token="session_token",
            price_quote_container_id="price_quote_container_id",
        )

        yield message
