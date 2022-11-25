from __future__ import annotations

import datetime
import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest
from redis import asyncio as aioredis

from snowfall.project.junction.service.providers.save_a_train import (
    adapter,
    cache,
    train_stations,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.save_a_train import client


def load_json_fixture(
    file_name: str,
) -> dict[str, Any]:
    file_path = filesystem.resource_path(
        package="snowfall.project.junction.service.providers.save_a_train.conftest",
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    with open(file_path) as file_handle:
        return json.load(file_handle)


@pytest.fixture
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture
def save_a_train_client(http_client: httpx.AsyncClient) -> client.SATClient:
    return client.SATClient(  # nosec
        email="test@snowfall.com",
        password="secret",
        password_search="secret",
        token="token",
        api_url="https://test_url",
        api_search_url="https://test_url",
        api_search_timeout=10,
        api_search_requests_limit=1,
        client=http_client,
    )


@pytest.fixture
def train_station_repository() -> train_stations.TrainStationRepository:
    return train_stations.TrainStationRepository(
        train_stations=[],
    )


@pytest.fixture
def save_a_train_adapter(
    save_a_train_client: client.SATClient,
    train_station_repository: train_stations.TrainStationRepository,
    redis_client: aioredis.Redis[bytes],
) -> adapter.SaveATrainAdapter:
    return adapter.SaveATrainAdapter(
        save_a_train_client=save_a_train_client,
        train_station_repository=train_station_repository,
        offers_cache=cache.OffersCache(
            client=redis.Client(redis_client),
        ),
        ttl=datetime.timedelta(minutes=1),
    )
