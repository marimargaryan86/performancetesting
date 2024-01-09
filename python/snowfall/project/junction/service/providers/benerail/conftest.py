from __future__ import annotations

import datetime
from collections.abc import AsyncIterator
from typing import Any
from unittest import mock

import aiofiles
import httpx
import orjson
import pytest
from google.protobuf.timestamp_pb2 import Timestamp
from motor import core
from redis import asyncio as aioredis

from snowfall.project.junction.provider import notifications as base_notifications
from snowfall.project.junction.provider.cabin_classes import CabinMappingRepository
from snowfall.project.junction.service.providers.benerail import adapter, consumer
from snowfall.project.junction.service.providers.benerail.cache import OffersCache
from snowfall.project.junction.service.providers.benerail.train_stations import (
    TrainStationRepository,
)
from snowfall.project.junction.service.providers.benerail.v1 import (
    amqp_pb2 as br_amqp_pb2,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.benerail import client
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient
from snowfall.vendor.zendesk.client import ZendeskClient

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


@pytest.fixture()
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def zendesk_client(http_client: httpx.AsyncClient) -> ZendeskClient:
    return ZendeskClient(
        base_url="https://test.api.com",
        api_key="somefakeapikey123",
        http_client=http_client,
        env="local",
    )


@pytest.fixture()
def consumer_obj() -> mock.AsyncMock:
    mock_consumer = mock.create_autospec(amqp_consumer.Consumer)
    return mock_consumer.return_value


@pytest.fixture()
def notifier() -> mock.AsyncMock:
    mock_notifier = mock.create_autospec(base_notifications.Notifier)
    return mock_notifier.return_value


@pytest.fixture()
def booking_storage() -> mock.AsyncMock:
    mock_booking_storage = mock.create_autospec(filesystem.Storage)
    return mock_booking_storage.return_value


@pytest.fixture()
def notifications_consumer(
    consumer_obj: mock.AsyncMock,
    benerail_client: client.BenerailClient,
    notifier: mock.AsyncMock,
    booking_storage: mock.AsyncMock,
    zendesk_client: ZendeskClient,
) -> consumer.NotificationsConsumer:
    return consumer.NotificationsConsumer(
        consumer_obj=consumer_obj,
        benerail_client=benerail_client,
        notifier=notifier,
        booking_storage=booking_storage,
        zendesk_client=zendesk_client,
        zendesk_booked_ticket_group_id=123,
        retry_ttl=datetime.timedelta(hours=1),
    )


@pytest.fixture()
def message() -> types.Message[br_amqp_pb2.BookingNotificationTask]:
    created_at = Timestamp()
    created_at.GetCurrentTime()

    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as mock_message:
        message = mock_message.return_value
        message.body.journey_id = "journey_id"
        message.body.order_id = "order_id"
        message.body.booking_id = "booking_id"
        message.body.br_booking_id = "br_booking_id"
        message.body.br_dnr = "br_dnr"
        message.body.passenger_name_record = "passenger_name_record"
        message.body.departure_at = str(
            datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
        )
        message.body.created_at = created_at

        return message


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
