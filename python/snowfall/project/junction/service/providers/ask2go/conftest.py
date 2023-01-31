from __future__ import annotations

import contextlib
import datetime
import hashlib
import json
from collections.abc import AsyncIterator
from typing import Any, Iterator, cast

import httpx
import mongomock_motor
import pytest
import pytest_httpx
import structlog
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.provider import airports, cabin_classes, notifications
from snowfall.project.junction.service.providers.ask2go import (
    booking,
    cache,
    criteria,
    pricing,
    search,
    transformer,
    validator,
)
from snowfall.stdlib import h3
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.ask2go import client


def load_json_fixture(
    file_name: str,
) -> dict[str, Any]:
    file_path = filesystem.resource_path(
        package="snowfall.project.junction.service.providers.ask2go.conftest",
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    with open(file_path) as file_handle:
        return json.load(file_handle)


class MagicMocker(object):
    def __init__(self, httpx_mock: pytest_httpx.HTTPXMock):
        self._mock = httpx_mock
        self._path = ""
        self._logger = structlog.get_logger(__name__)

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
            fixture = load_json_fixture(filename)
        except FileNotFoundError:
            self._logger.info("File does not exist", file=filename)
            return

        self._mock.add_response(
            method=request.method,
            json=fixture,
            url=request.url,
        )


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


@pytest.fixture
async def airport_repository() -> airports.AirportRepository:
    loader = filesystem.PkgLoader(__name__)

    return airports.AirportRepository(
        cast(list[dict[str, Any]], loader.load("airports.json")),
    )


@pytest.fixture
def magic_mocker(httpx_mock: pytest_httpx.HTTPXMock) -> MagicMocker:
    return MagicMocker(httpx_mock)


@pytest.fixture
async def http_client(magic_mocker: MagicMocker) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        event_hooks={"request": [magic_mocker.magic_loader]},
    ) as http_client:
        yield http_client


@pytest.fixture
def ask2go_client(http_client: httpx.AsyncClient) -> client.Ask2GoClient:
    return client.Ask2GoClient(
        api_base_url="https://test_url",
        api_booking_base_url="https://test_url",
        http_client=http_client,
    )


@pytest.fixture
def mongo_client() -> motor_asyncio.AsyncIOMotorClient:
    return mongomock_motor.AsyncMongoMockClient()


@pytest.fixture
def offer_validator() -> validator.OfferValidator:
    return validator.OfferValidator()


@pytest.fixture
def search_adapter(
    ask2go_client: client.Ask2GoClient,
    offer_validator: validator.OfferValidator,
) -> search.Adapter:
    return search.Adapter(
        ask2go_client=ask2go_client,
        offer_validator=offer_validator,
        poll_retries_limit=1,
        wait_time_between_polling=0,
    )


@pytest.fixture
def pricing_adapter(
    ask2go_client: client.Ask2GoClient,
) -> pricing.Adapter:
    return pricing.Adapter(
        ask2go_client=ask2go_client,
        poll_retries_limit=1,
        wait_time_between_polling=0,
    )


@pytest.fixture
def offer_transformer(
    airport_repository: airports.AirportRepository,
    provider_cabin_class_mapping: cabin_classes.CabinMappingRepository,
    redis_client: aioredis.Redis[bytes],
) -> transformer.OfferTransformer:
    return transformer.OfferTransformer(
        airport_repository=airport_repository,
        cabin_mapping_repository=provider_cabin_class_mapping,
        offer_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
        price_cache=cache.PriceQuoteCache(
            client=redis.Client(redis_client),
        ),
        offer_ttl=datetime.timedelta(days=1),
    )


@pytest.fixture
def h3_mapping_repository(
    airport_repository: airports.AirportRepository,
) -> h3.H3MappingRepository[airports.Airport]:
    return h3.H3MappingRepository[airports.Airport](
        mapping=airport_repository.all_(),
        resolution=7,
    )


@pytest.fixture
def criteria_generator(
    h3_mapping_repository: h3.H3MappingRepository[airports.Airport],
) -> criteria.CriteriaGenerator:
    return criteria.CriteriaGenerator(h3_mapping=h3_mapping_repository)


@pytest.fixture
def booking_handler(ask2go_client: client.Ask2GoClient) -> booking.BookingHandler:
    return booking.BookingHandler(
        ask2go_client=ask2go_client,
        notifier=notifications.LogNotifier(),
        override_double_booking_check=False,
    )


@pytest.fixture
def provider_cabin_class_mapping(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> cabin_classes.CabinMappingRepository:
    return cabin_classes.CabinMappingRepository(
        collection=mongo_client.test.provider_cabin_mapping,
    )
