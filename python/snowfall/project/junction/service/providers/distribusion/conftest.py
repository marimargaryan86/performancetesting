from __future__ import annotations

import datetime
import os
import typing
from collections.abc import AsyncIterator
from unittest import mock

import aiofiles
import httpx
import orjson
import pytest
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.providers.distribusion import (
    cache,
    pricing,
    stations,
)
from snowfall.project.junction.service.providers.distribusion.search.adapter import (
    DistribusionSearchAdapter,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.httpx_logger import with_logging
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

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
    mock_rate_limit_client = mock.create_autospec(
        RateLimitClient,
        spec_set=True,
        instance=True,
    )

    return client.DistribusionClient(
        api_base_url=API_BASE_URL,
        api_key="MkQQ6J6BO2ooqwZYpM6fUmDu6rGwWXP1obaQuITo",
        retailer_partner_number="431926",
        http_client=http_client,
        rate_limit_client=mock_rate_limit_client,
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
def price_quote_cache(redis_client: aioredis.Redis[bytes]) -> cache.PriceQuoteCache:
    return cache.PriceQuoteCache(
        client=redis.Client(redis_client),
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
def offer_ttl() -> datetime.timedelta:
    return datetime.timedelta(minutes=45)


@pytest.fixture()
def provider_company_id() -> str:
    return "provider_id"


@pytest.fixture()
def passenger_type() -> cache.PassengerType:
    return cache.PassengerType(
        type_name="ADT",
        type_code="ADT",
        min_age=18,
        max_age=99,
    )


@pytest.fixture()
def epxires_at() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(minutes=45)


@pytest.fixture()
def offer_details(
    passenger_type: cache.PassengerType,
    epxires_at: datetime.datetime,
) -> cache.OfferDetails:
    return cache.OfferDetails(
        expires_at=epxires_at,
        departure_station="departure_station",
        arrival_station="arrival_station",
        departure_time=datetime.datetime.now(tz=datetime.UTC),
        arrival_time=datetime.datetime.now(tz=datetime.UTC),
        marketing_carrier="marketing_carrier",
        passengers_age=[passenger_type.min_age],
        currency="EUR",
        price=100,
        fare_class="fare_class",
        passenger_types=[passenger_type],
    )


@pytest.fixture()
def price_quote_consumer(
    distribusion_client: client.DistribusionClient,
    consumer_obj: mock.AsyncMock,
    producer_obj: mock.AsyncMock,
    offer_ttl: datetime.timedelta,
    redis_client: aioredis.Redis[bytes],
    provider_company_id: str,
) -> pricing.PriceQuoteConsumer:
    return pricing.PriceQuoteConsumer(
        distribusion_client=distribusion_client,
        consumer_obj=consumer_obj,
        producer_obj=producer_obj,
        offer_cache=cache.OffersCache(
            client=redis.Client(redis_client),
        ),
        price_quote_cache=cache.PriceQuoteCache(
            client=redis.Client(redis_client),
        ),
        ttl=offer_ttl,
        provider_company_id=provider_company_id,
    )


@pytest.fixture()
async def option_id(
    price_quote_consumer: pricing.PriceQuoteConsumer,
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


async def load_file_fixture(
    file_name: str,
) -> typing.Any:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.distribusion.conftest",
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    async with aiofiles.open(file_path) as json_file:
        return orjson.loads(await json_file.read())
