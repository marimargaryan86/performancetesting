import contextlib
import datetime
import hashlib
import json
from collections.abc import AsyncIterator
from typing import Any, Iterator, cast

import aioredis
import httpx
import pytest
import pytest_httpx
import structlog

from snowfall.project.junction.service.providers.ask2go import (
    adapter,
    airports,
    booking,
    cache,
    criteria,
    notifications,
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
    loader = filesystem.PkgLoader(
        "snowfall.project.junction.service.providers.ask2go.airports",
    )

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
def offer_validator() -> validator.OfferValidator:
    return validator.OfferValidator()


@pytest.fixture
def ask2go_adapter(
    ask2go_client: client.Ask2GoClient,
    offer_validator: validator.OfferValidator,
) -> adapter.Ask2GoAdapter:
    return adapter.Ask2GoAdapter(
        ask2go_client=ask2go_client,
        offer_validator=offer_validator,
        poll_retries_limit=1,
        wait_time_between_polling=0,
    )


@pytest.fixture
def offer_transformer(
    airport_repository: airports.AirportRepository,
    redis_client: aioredis.Redis,
) -> transformer.OfferTransformer:
    return transformer.OfferTransformer(
        airport_repository=airport_repository,
        offer_cache=cache.OfferCache(
            client=redis.Client[bytes](redis_client),
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
    )
