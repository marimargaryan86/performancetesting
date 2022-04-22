import datetime
from collections.abc import AsyncIterator
from typing import Any, Mapping, Sequence

import httpx
import pytest

from snowfall.junction.providers.ask2go import adapter, airports, criteria, h3
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.models import common


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


@pytest.fixture
async def airport_repository(
    airport_coordinates: Mapping[str, Mapping[str, Any]],
    ask2go_airports: Sequence[common.Airport],
) -> airports.AirportRepository:
    return airports.AirportRepository(
        coordinates=airport_coordinates,
        airports=ask2go_airports,
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
def ask2go_adapter(
    ask2go_client: client.Ask2GoClient,
    airport_repository: airports.AirportRepository,
) -> adapter.Ask2GoAdapter:
    return adapter.Ask2GoAdapter(
        ask2go_client=ask2go_client,
        airport_repository=airport_repository,
        ttl=datetime.timedelta(days=1),
    )


@pytest.fixture
def ask2go_airports() -> list[common.Airport]:
    return [
        common.Airport(iata="ARN", airport_name="Arlanda"),
        common.Airport(iata="LHR", airport_name="Heathrow"),
        common.Airport(iata="DMM", airport_name="King Fahad International"),
        common.Airport(iata="PBM", airport_name="Zanderij International"),
        common.Airport(iata="ORG"),
        common.Airport(iata="WRY", airport_name="Westray"),
        common.Airport(iata="PPW", airport_name="Papa Westray"),
    ]


@pytest.fixture
def airport_coordinates() -> Mapping[str, Mapping[str, Any]]:
    loader = filesystem.PkgLoader("snowfall.junction.providers.ask2go.airports")

    return loader.load("airport_coordinates.json")


@pytest.fixture
def h3_mapping_repository(
    airport_coordinates: Mapping[str, Mapping[str, Any]],
    ask2go_airports: Sequence[common.Airport],
) -> h3.H3MappingRepository[airports.Airport]:
    return h3.H3MappingRepository[airports.Airport](
        mapping=airports.create_airports_mapping(
            coordinates=airport_coordinates,
            airports=ask2go_airports,
        ),
        resolution=7,
    )


@pytest.fixture
def criteria_generator(
    h3_mapping_repository: h3.H3MappingRepository[airports.Airport],
) -> criteria.CriteriaGenerator:
    return criteria.CriteriaGenerator(h3_mapping=h3_mapping_repository)
