from __future__ import annotations

import datetime
import json
from collections.abc import AsyncIterator, Mapping
from typing import Any
from unittest import mock

import aiofiles
import httpx
import orjson
import pytest
from google.protobuf.timestamp_pb2 import Timestamp
from redis import asyncio as aioredis

from snowfall.project.junction.go.v1.models_pb2 import Point
from snowfall.project.junction.rocket.service.providers.direct_ferries import (
    cache,
    config,
    port,
    route,
    searches,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.v1 import date_pb2
from snowfall.stdlib.v1.latlng_pb2 import LatLng
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.clients import auth, base

CLIENT_SECRET = "1jhj5gve52o7b8puafh0n218iq77u2vva8oosemi063a9g62e3qg"
CLIENT_ID = "3r2ha5jopuaphv9fctntqtraso"
API_URL = "https://tf-test-affiliate-api-sandbox.auth.eu-west-1.amazoncognito.com"


@pytest.fixture()
def origin() -> Mapping[str, Any]:
    return {
        "id": "NLMDK",
        "name": "Hook of Holland",
        "latitude": 51.9754793,
        "longitude": 4.1255803,
        "timezone": "Europe/Amsterdam",
    }


@pytest.fixture()
def destination() -> Mapping[str, Any]:
    return {
        "id": "GBHRW",
        "name": "Harwich",
        "latitude": 51.94743,
        "longitude": 1.2533101,
        "timezone": "Europe/London",
    }


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def df_client(
    http_client: httpx.AsyncClient,
) -> client.DfHttpClient:
    return client.DfHttpClient(
        http_client=http_client,
        auth_client=auth.AuthClient(
            http_client=http_client,
            client_secret=CLIENT_SECRET,
            api_url=API_URL,
            client_id=CLIENT_ID,
        ),
        config=base.ClientConfig(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            api_url="https://sandbox-api.test.directferriesconnect.com",
            partner_code="F5152",
            timeout=40,
        ),
    )


@pytest.fixture()
async def ports() -> list[port.Port]:
    return port.load_ports()


@pytest.fixture()
async def routes() -> list[route.Route]:
    return route.load_routes()


@pytest.fixture()
async def generator(
    df_client: client.DfHttpClient,
    redis_client: aioredis.Redis[bytes],
) -> searches.SearchResultGenerator:
    return searches.SearchResultGenerator(
        df_client=df_client,
        offers_cache=cache.OffersCache(client=redis.Client[bytes](redis_client)),
        ttl=datetime.timedelta(
            minutes=config._OFFER_TTL_DEFAULT_MINUTES,  # noqa: SLF001
        ),
    )


@pytest.fixture()
def one_way_search(
    origin: Mapping[str, Any],
    destination: Mapping[str, Any],
) -> models_pb2.Search:
    return generate_search(
        departure_date=departure_date(),
        return_date=None,
        origin=origin,
        destination=destination,
    )


@pytest.fixture()
def mock_one_way_search(
    origin: Mapping[str, Any],
    destination: Mapping[str, Any],
    mock_departure_date: Timestamp,
) -> models_pb2.Search:
    return generate_search(
        departure_date=mock_departure_date,
        return_date=None,
        origin=origin,
        destination=destination,
    )


@pytest.fixture()
def criteria_generator() -> searches.CriteriaGenerator:
    return searches.CriteriaGenerator()


@pytest.fixture()
async def mock_one_way_response() -> AsyncIterator[Any]:
    with mock.patch(
        "snowfall.vendor.direct_ferries.clients.quote.QuoteClient._make_request",
    ) as mock_request:
        response = await load_file_fixture("one_way_response.json")
        response_json = json.dumps(response)
        mock_response = httpx.Response(200, content=response_json)
        mock_request.return_value = mock_response
        yield mock_request


@pytest.fixture()
def mock_round_trip_search(
    origin: Mapping[str, Any],
    destination: Mapping[str, Any],
    mock_departure_date: Timestamp,
    mock_return_date: Timestamp,
) -> models_pb2.Search:
    return generate_search(
        departure_date=mock_departure_date,
        return_date=mock_return_date,
        origin=origin,
        destination=destination,
    )


@pytest.fixture()
async def mock_round_trip_response() -> AsyncIterator[Any]:
    with mock.patch(
        "snowfall.vendor.direct_ferries.clients.quote.QuoteClient._make_request",
    ) as mock_request:
        response = await load_file_fixture("round_trip_response.json")
        response_json = json.dumps(response)
        mock_response = httpx.Response(200, content=response_json)
        mock_request.return_value = mock_response
        yield mock_request


@pytest.fixture()
def mock_departure_date() -> Timestamp:
    year = 2024
    month = 4
    day = 15
    hour = 5
    date = datetime.datetime(year, month, day, hour, 0, 0)  # noqa: DTZ001
    timestamp = Timestamp()
    timestamp.FromDatetime(date)
    return timestamp


@pytest.fixture()
def mock_return_date() -> Timestamp:
    year = 2024
    month = 4
    day = 17
    hour = 5
    date = datetime.datetime(year, month, day, hour, 0, 0)  # noqa: DTZ001
    timestamp = Timestamp()
    timestamp.FromDatetime(date)
    return timestamp


@pytest.fixture()
def round_trip_search(
    origin: Mapping[str, Any],
    destination: Mapping[str, Any],
) -> models_pb2.Search:
    return generate_search(
        departure_date=departure_date(),
        return_date=return_date(),
        origin=origin,
        destination=destination,
    )


def adult_passenger() -> models_pb2.Passenger:
    return models_pb2.Passenger(date_of_birth=date_pb2.Date(year=1990, month=1, day=1))


def child_passenger() -> models_pb2.Passenger:
    now = datetime.datetime.now(tz=datetime.UTC)
    return models_pb2.Passenger(
        date_of_birth=date_pb2.Date(year=now.year - 7, month=1, day=1),
    )


def generate_search(
    departure_date: Timestamp,
    origin: Mapping[str, Any],
    destination: Mapping[str, Any],
    return_date: Timestamp | None,
) -> models_pb2.Search:
    return models_pb2.Search(
        ferry=models_pb2.Ferry(
            departure_after=departure_date,
            return_date=return_date,
            vehicles=[
                models_pb2.Vehicle(type_id=models_pb2.Vehicle.TypeId.TYPE_ID_CAR),
            ],
            origin=Point(
                coordinates=LatLng(
                    latitude=origin["latitude"],
                    longitude=origin["longitude"],
                ),
            ),
            destination=Point(
                coordinates=LatLng(
                    latitude=destination["latitude"],
                    longitude=destination["longitude"],
                ),
            ),
            passengers=[adult_passenger(), child_passenger()],
        ),
    )


def departure_date() -> Timestamp:
    now = datetime.datetime.now(tz=datetime.UTC)
    month = (now.month % 12) + 1
    year = now.year + 1 if month == 1 else now.year
    day = 15
    hour = 5
    date = datetime.datetime(year, month, day, hour, 0, 0)  # noqa: DTZ001
    timestamp = Timestamp()
    timestamp.FromDatetime(date)
    return timestamp


def return_date() -> Timestamp:
    now = datetime.datetime.now(tz=datetime.UTC)
    month = (now.month % 12) + 1
    year = now.year + 1 if month == 1 else now.year
    day = 17
    hour = 5
    date = datetime.datetime(year, month, day, hour, 0, 0)  # noqa: DTZ001
    timestamp = Timestamp()
    timestamp.FromDatetime(date)
    return timestamp


async def load_file_fixture(
    file_name: str,
) -> Any:
    file_path = filesystem.resource_path(
        package="snowfall.project.junction.rocket.service.providers.direct_ferries.conftest",
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    async with aiofiles.open(file_path) as json_file:
        return orjson.loads(await json_file.read())
