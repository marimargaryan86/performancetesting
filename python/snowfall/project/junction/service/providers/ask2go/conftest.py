import datetime
import json
from collections.abc import AsyncIterator
from typing import Any, cast

import aioredis
import httpx
import pytest

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
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
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
