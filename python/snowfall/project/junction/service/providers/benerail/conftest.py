from __future__ import annotations

import datetime
from typing import Any
from unittest import mock

import aiofiles
import httpx
import orjson
import pytest
from motor import core
from redis import asyncio as aioredis

from snowfall.project.junction.provider.cabin_classes import CabinMappingRepository
from snowfall.project.junction.service.providers.benerail import adapter
from snowfall.project.junction.service.providers.benerail.cache import OffersCache
from snowfall.project.junction.service.providers.benerail.train_stations import (
    TrainStationRepository,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.benerail import client
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

_TIMEOUT = 50.0
API_BASE_URL = "https://benerail-stg-test.net"


@pytest.fixture()
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture()
def benerail_client(http_client: httpx.AsyncClient) -> client.BenerailClient:
    mock.create_autospec(
        RateLimitClient,
        spec_set=True,
        instance=True,
    )

    return client.BenerailClient(
        subscription_key="test",
        base_url=API_BASE_URL,
        http_client=http_client,
    )


@pytest.fixture()
def train_station_repository() -> TrainStationRepository:
    return TrainStationRepository(
        train_stations=[],
    )


@pytest.fixture()
async def provider_cabin_class_mapping(
    mongo_client: core.AgnosticClient,
) -> CabinMappingRepository:
    return CabinMappingRepository(
        collection=mongo_client.test.provider_cabin_mapping,
    )


@pytest.fixture()
def benerail_adapter(
    benerail_client: client.BenerailClient,
    train_station_repository: TrainStationRepository,
    provider_cabin_class_mapping: CabinMappingRepository,
    redis_client: aioredis.Redis[bytes],
) -> adapter.BenerailOffersAdapter:
    return adapter.BenerailOffersAdapter(
        offers_cache=OffersCache(
            client=redis.Client(redis_client),
        ),
        benerail_client=benerail_client,
        train_station_repository=train_station_repository,
        ttl=datetime.timedelta(),
        provider_cabin_class_mapping=provider_cabin_class_mapping,
    )


async def load_file_fixture(
    file_name: str,
) -> Any:
    file_path = filesystem.resource_path(
        package=__name__,
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    async with aiofiles.open(file_path) as json_file:
        return orjson.loads(await json_file.read())
