from __future__ import annotations

import contextlib
import datetime
import hashlib
from collections.abc import AsyncIterator, Iterator
from typing import Any
from unittest import mock

import aiofiles
import httpx
import orjson
import pytest
import pytest_httpx
from motor import core
from redis import asyncio as aioredis

from snowfall.project.junction.provider import airports, cabin_classes, notifications
from snowfall.project.junction.service.providers.ask2go import (
    booking,
    cache,
    criteria,
    pricing,
    transformer,
)
from snowfall.project.junction.service.providers.ask2go.location_repository import (
    LocationRepository,
)
from snowfall.project.junction.service.providers.ask2go.train_stations import (
    TrainStation,
    TrainStationRepository,
)
from snowfall.stdlib import h3
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.adapter import Adapter
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient


@pytest.fixture()
def train_station_repository() -> TrainStationRepository:
    return TrainStationRepository([])


@pytest.fixture()
def location_repository(
    airport_repository: airports.AirportRepository,
    train_station_repository: TrainStationRepository,
) -> LocationRepository:
    return LocationRepository(airport_repository, train_station_repository)


async def load_json_fixture(
    file_name: str,
) -> dict[str, Any]:
    file_path = filesystem.resource_path(
        package="snowfall.project.junction.service.providers.ask2go.conftest",
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    async with aiofiles.open(file_path) as file_handle:
        return orjson.loads(await file_handle.read())


class MagicMocker(object):
    def __init__(self, httpx_mock: pytest_httpx.HTTPXMock):
        self._mock = httpx_mock
        self._path = ""
        self._logger = stdout.get_logger()

    @contextlib.contextmanager
    def with_fixture_path(self, path: str) -> Iterator[None]:
        self._path = path

        try:
            yield
        finally:
            self._path = ""

    async def magic_loader(self, request: httpx.Request) -> None:
        filename = "{method}_{endpoint}".format(
            method=request.method.lower(),
            endpoint=request.url.path.removeprefix("/api/").lower().replace("/", "_"),
        )

        if self._path:
            filename = "{sub_path}/{file}".format(sub_path=self._path, file=filename)

        if request.content:
            filename = "{file}_{hash}".format(
                file=filename,
                hash=hashlib.md5(request.content, usedforsecurity=False).hexdigest(),
            )

        try:
            fixture = await load_json_fixture(filename)
        except FileNotFoundError:
            self._logger.info("File does not exist", file=filename)
            return

        self._mock.add_response(
            method=request.method,
            json=fixture,
            url=request.url,
        )


@pytest.fixture()
def assert_all_responses_were_requested() -> bool:
    return False


@pytest.fixture()
async def airport_repository() -> airports.AirportRepository:
    loader = filesystem.PkgLoader("snowfall.data")

    airports_list: list[dict[str, Any]] = loader.load("airports.json")
    return airports.AirportRepository(airports_list)


@pytest.fixture()
def magic_mocker(httpx_mock: pytest_httpx.HTTPXMock) -> MagicMocker:
    return MagicMocker(httpx_mock)


@pytest.fixture()
async def http_client(magic_mocker: MagicMocker) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        event_hooks={"request": [magic_mocker.magic_loader]},
    ) as http_client:
        yield http_client


@pytest.fixture()
def ask2go_client(http_client: httpx.AsyncClient) -> client.Ask2GoClient:
    mock_rate_limit_client = mock.create_autospec(
        RateLimitClient,
        spec_set=True,
        instance=True,
    )
    return client.Ask2GoClient(
        api_base_url="https://test_url",
        api_booking_base_url="https://test_url",
        http_client=http_client,
        rate_limit_client=mock_rate_limit_client,
    )


@pytest.fixture()
def search_adapter(
    ask2go_client: client.Ask2GoClient,
) -> Adapter:
    return Adapter(
        ask2go_client=ask2go_client,
        poll_retries_limit=1,
        wait_time_between_polling=0,
    )


@pytest.fixture()
def pricing_adapter(
    ask2go_client: client.Ask2GoClient,
) -> pricing.Adapter:
    return pricing.Adapter(
        ask2go_client=ask2go_client,
        poll_retries_limit=1,
        wait_time_between_polling=0,
    )


@pytest.fixture()
def offer_transformer(
    location_repository: LocationRepository,
    provider_cabin_class_mapping: cabin_classes.CabinMappingRepository,
    redis_client: aioredis.Redis[bytes],
) -> transformer.OfferTransformer:
    return transformer.OfferTransformer(
        repository=location_repository,
        cabin_mapping_repository=provider_cabin_class_mapping,
        offer_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
        price_cache=cache.PriceQuoteCache(
            client=redis.Client(redis_client),
        ),
        offer_ttl=datetime.timedelta(days=1),
    )


@pytest.fixture()
def h3_mapping_repository(
    airport_repository: airports.AirportRepository,
) -> h3.H3MappingRepository[airports.Airport]:
    return h3.H3MappingRepository[airports.Airport](
        mapping=airport_repository.all_(),
        resolution=7,
    )


@pytest.fixture()
def stations_h3_mapping(
    train_station_repository: TrainStationRepository,
) -> h3.H3MappingRepository[TrainStation]:
    return h3.H3MappingRepository[TrainStation](
        mapping=train_station_repository.all_(),
        resolution=7,
    )


@pytest.fixture()
def criteria_generator(
    h3_mapping_repository: h3.H3MappingRepository[airports.Airport],
    stations_h3_mapping: h3.H3MappingRepository[TrainStation],
) -> criteria.CriteriaGenerator:
    return criteria.CriteriaGenerator(
        h3_mapping=h3_mapping_repository,
        stations_h3_mapping=stations_h3_mapping,
        reseller_id_affiliate_id_map={"test-reseller": "test-affiliate"},
    )


@pytest.fixture()
async def storage() -> AsyncIterator[filesystem.Storage]:
    async with filesystem.Storage.from_dsn("memory://") as storage_obj:
        yield storage_obj


@pytest.fixture()
def offer_cache(redis_client: aioredis.Redis[bytes]) -> cache.OfferCache:
    return cache.OfferCache(client=redis.Client(redis_client))


@pytest.fixture()
def booking_handler(
    ask2go_client: client.Ask2GoClient,
    offer_cache: cache.OfferCache,
    storage: filesystem.Storage,
) -> booking.BookingHandler:
    return booking.BookingHandler(
        ask2go_client=ask2go_client,
        notifier=notifications.LogNotifier(),
        booking_storage=storage,
        override_double_booking_check=False,
        offer_cache=offer_cache,
    )


@pytest.fixture()
async def provider_cabin_class_mapping(
    mongo_client: core.AgnosticClient,
) -> cabin_classes.CabinMappingRepository:
    return cabin_classes.CabinMappingRepository(
        collection=mongo_client.test.provider_cabin_mapping,
    )
