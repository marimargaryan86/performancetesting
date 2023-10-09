from __future__ import annotations

import datetime
from collections.abc import AsyncIterator
from typing import Any

import aiofiles
import httpx
import orjson
import pytest
from aio_pika import Connection, connection
from motor import core
from redis import asyncio as aioredis

from snowfall.project.junction.provider import cabin_classes, notifications
from snowfall.project.junction.service.providers.save_a_train import (
    adapter,
    cache,
    train_stations,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
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
def provider_cabin_class_mapping(
    mongo_client: core.AgnosticClient,
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
