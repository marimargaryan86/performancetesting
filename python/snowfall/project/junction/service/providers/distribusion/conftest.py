from __future__ import annotations

import datetime
import os

import httpx
import pytest
from redis import asyncio as aioredis

from snowfall.project.junction.service.providers.distribusion import cache, stations
from snowfall.project.junction.service.providers.distribusion.search.adapter import (
    DistribusionSearchAdapter,
)
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.httpx_logger import with_logging

TIMEOUT = 10.0
API_BASE_URL = "https://api.demo.distribusion.com"

disable_by_default = pytest.mark.skipif(
    os.getenv("DISTRIBUSION_TESTS") != "ENABLED",
    reason="To enable set env variable DISTRIBUSION_TESTS=ENABLED",
)


@pytest.fixture()
def http_client() -> httpx.AsyncClient:
    return with_logging(httpx.AsyncClient(timeout=TIMEOUT))


@pytest.fixture()
def distribusion_client(http_client: httpx.AsyncClient) -> client.DistribusionClient:
    return client.DistribusionClient(
        api_base_url=API_BASE_URL,
        api_key="MkQQ6J6BO2ooqwZYpM6fUmDu6rGwWXP1obaQuITo",
        retailer_partner_number="431926",
        http_client=http_client,
    )


@pytest.fixture()
async def station_repository() -> stations.StationRepository:
    return stations.StationRepository(
        stations=await stations.load_stations(),
    )


@pytest.fixture()
def offer_cache(redis_client: aioredis.Redis[bytes]) -> cache.OffersCache:
    return cache.OffersCache(
        client=redis.Client(redis_client),
    )


@pytest.fixture()
def distribusion_search_adapter(
    distribusion_client: client.DistribusionClient,
    offer_cache: cache.OffersCache,
) -> DistribusionSearchAdapter:
    return DistribusionSearchAdapter(
        distribusion_client=distribusion_client,
        offers_cache=offer_cache,
        ttl=datetime.timedelta(minutes=10),
    )
