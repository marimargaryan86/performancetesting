from collections.abc import AsyncIterator
from typing import Any, cast
from unittest import mock

import aiofiles
import httpx
import orjson
import pytest
import pytest_httpx
from motor import core

from snowfall.project.junction.content.service.benerail import adapter, train_stations
from snowfall.project.junction.provider import cabin_classes
from snowfall.stdlib import h3
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models.enumeration.response import RcodesResponse
from snowfall.vendor.benerail.models.trip_offers import trip_offers
from snowfall.vendor.benerail.models.trips import trips

API_BASE_URL = "http://benerail-test"


async def load_json_fixture(
    file_name: str,
    package: str | None = None,
) -> dict[str, Any]:
    if not package:
        package = __name__

    file_path = filesystem.resource_path(
        package=package,
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    async with aiofiles.open(file_path) as file_handle:
        return orjson.loads(await file_handle.read())


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def benerail_client(http_client: httpx.AsyncClient) -> client.BenerailClient:
    return client.BenerailClient(
        subscription_key="",
        base_url=API_BASE_URL,
        http_client=http_client,
    )


@pytest.fixture()
async def provider_cabin_class_mapping(
    mongo_client: core.AgnosticClient,
) -> cabin_classes.CabinMappingRepository:
    return cabin_classes.CabinMappingRepository(
        collection=mongo_client.test.provider_cabin_mapping,
    )


@pytest.fixture()
async def stations() -> list[train_stations.TrainStation]:
    return train_stations.load_train_stations()


@pytest.fixture()
def train_station_repository(
    stations: list[train_stations.TrainStation],
) -> train_stations.TrainStationRepository:
    return train_stations.TrainStationRepository(stations=stations)


@pytest.fixture()
def station_mapping(
    stations: list[train_stations.TrainStation],
) -> h3.H3MappingRepository[train_stations.TrainStation]:
    return h3.H3MappingRepository[train_stations.TrainStation](
        mapping=stations,
        resolution=8,
    )


@pytest.fixture()
async def trip_with_trip_offer() -> adapter.TripWithTripOffer:
    data = await load_json_fixture("trip_with_trip_offer.json")
    return adapter.TripWithTripOffer(
        trip=trips.Trip(**data["trip"]),
        trip_offer=trip_offers.TripOffer(**data["trip_offer"]),
    )


@pytest.fixture()
def benerail_adapter(
    benerail_client: client.BenerailClient,
    trip_with_trip_offer: adapter.TripWithTripOffer,
) -> adapter.BenerailAdapter:
    async def _mock_adapter_results() -> AsyncIterator[adapter.TripWithTripOffer]:  # noqa: WPS430
        for _ in range(1):
            yield trip_with_trip_offer

    adapter_mock = mock.MagicMock()
    adapter_mock.search_with_trip_offers.return_value = _mock_adapter_results()
    return cast(adapter.BenerailAdapter, adapter_mock)


@pytest.fixture()
async def train_rcode_response(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> RcodesResponse:
    json = await load_json_fixture(
        "train_type_rcode.json",
        "snowfall.vendor.benerail.client",
    )
    httpx_mock.add_response(
        url="{api_base_url}/rcode/rcode/value/{urn}".format(
            api_base_url=API_BASE_URL,
            urn="urn:itti:train_type:ICE",
        ),
        method="GET",
        json=json,
    )
    return RcodesResponse.parse_obj(json)


@pytest.fixture()
async def cabin_class_rcode_response(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> RcodesResponse:
    json = await load_json_fixture(
        "cabin_class_rcode.json",
        "snowfall.vendor.benerail.client",
    )
    httpx_mock.add_response(
        url="{api_base_url}/rcode/rcode/value/{urn}".format(
            api_base_url=API_BASE_URL,
            urn="urn:taco:class:2",
        ),
        method="GET",
        json=json,
    )
    return RcodesResponse.parse_obj(json)
