from __future__ import annotations

import datetime
import json
import uuid
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Any
from unittest import mock

import aiofiles
import httpx
import orjson
import pytest
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.provider import airports
from snowfall.project.junction.service.providers.ba_ndc import cache, pricing
from snowfall.project.junction.service.providers.ba_ndc.search import adapter
from snowfall.project.junction.service.providers.ba_ndc.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.vendor.ba_ndc import client
from snowfall.vendor.ba_ndc.adapters.offers_response_adapter import (
    OffersResponseAdapter,
)
from snowfall.vendor.ba_ndc.models import (
    response_priced_offer_schemas,
)
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

_TIMEOUT = 50.0
API_BASE_URL = "https://ndc.junction.dev"


@pytest.fixture()
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=_TIMEOUT)


@pytest.fixture()
def ba_ndc_client(http_client: httpx.AsyncClient) -> client.BaNdcClient:
    mock_rate_limit_client = mock.create_autospec(
        RateLimitClient,
        spec_set=True,
        instance=True,
    )

    return client.BaNdcClient(
        api_base_url=API_BASE_URL,
        api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXRhaWxlcl9pZCI6MTIzLCJleHBpcmVzIjoxNzEyMjMyODU5LCJpYXQiOjE3MDc5MjUyOTd9.XIB4NHPiOXlXqpEflxedoy06OPCDyyFijGuoAmEKHBo",
        http_client=http_client,
        rate_limit_clients=(mock_rate_limit_client,),
    )


@pytest.fixture()
async def airport_repository() -> airports.AirportRepository:
    loader = filesystem.PkgLoader("snowfall.data")

    airports_list: list[dict[str, Any]] = loader.load("airports.json")
    return airports.AirportRepository(airports_list)


@pytest.fixture()
def search_adapter(
    ba_ndc_client: client.BaNdcClient,
    airport_repository: airports.AirportRepository,
    redis_client: aioredis.Redis[bytes],
) -> adapter.BaNdcSearchAdapter:
    return adapter.BaNdcSearchAdapter(
        ba_ndc_client=ba_ndc_client,
        airport_repository=airport_repository,
        offers_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
    )


def search_task_from_offer(
    offer_adapter: OffersResponseAdapter,
) -> amqp_pb2.SearchCriteriaTask | None:
    offer = offer_adapter.get_offers()[0]
    first_segment = offer_adapter.get_segment_by_id(offer.trips[0].segment_ids[0])
    last_segment = offer_adapter.get_segment_by_id(offer.trips[0].segment_ids[-1])

    if first_segment and last_segment:
        return amqp_pb2.SearchCriteriaTask(
            offer_search_id=str(uuid.uuid4()),
            segments=[
                models_pb2.Segment(
                    id=str(uuid.uuid4()),
                    legs=get_legs(offer_adapter, offer_segment_id),
                )
                for trip in offer.trips
                for offer_segment_id in trip.segment_ids
            ],
            criteria=amqp_pb2.Criteria(
                origin_iata=first_segment.origin.code or "",
                destination_iata=last_segment.destination.code or "",
                outbound_departure=protobuf.datetime_to_protobuf_datetime(
                    first_segment.departure_date_time.replace(
                        tzinfo=datetime.UTC,
                    ),
                ),
                adults=1,
                children=0,
                infants=0,
            ),
            session_token=str(uuid.uuid4()),
        )

    return None


def get_legs(
    offer_adapter: OffersResponseAdapter,
    offer_segment_id: str,
) -> list[models_pb2.Leg]:
    offer_segment = offer_adapter.get_segment_by_id(offer_segment_id)

    if offer_segment:
        return [
            models_pb2.Leg(
                id=str(uuid.uuid4()),
                origin=models_pb2.Point(
                    time_zone="Europe/London",
                ),
                destination=models_pb2.Point(
                    time_zone="Europe/London",
                ),
                departure_at=protobuf.datetime_to_protobuf(
                    offer_segment.departure_date_time,
                ),
                arrival_at=protobuf.datetime_to_protobuf(
                    offer_segment.arrival_date_time,
                ),
                type=models_pb2.Schedule.Type.TYPE_AIR,
            ),
        ]

    return []


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


@pytest.fixture()
def passengers() -> list[cache.OfferDetailsPassenger]:
    return [cache.OfferDetailsPassenger(identifier="PA0", passenger_type="adult")]


@pytest.fixture()
def penalties() -> list[cache.OfferPenalty]:
    return [
        cache.OfferPenalty(
            penalty_type="change",
            price=cache.Price(
                amount="10.00",
                currency="EUR",
            ),
        ),
    ]


@pytest.fixture()
def consumer_obj() -> mock.AsyncMock:
    mock_consumer = mock.create_autospec(amqp_consumer.Consumer)
    return mock_consumer.return_value


@pytest.fixture()
def producer_obj() -> mock.AsyncMock:
    mock_producer = mock.create_autospec(producer.Producer)
    return mock_producer.return_value


@pytest.fixture()
def expires_at() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(minutes=30)


@pytest.fixture()
def offer_details(
    expires_at: datetime.datetime,
) -> cache.OfferDetails:
    return cache.OfferDetails(
        offer_id=uuid.uuid4(),
        is_international_flight=True,
        has_flight_with_usa_destination=True,
        expires_at=expires_at,
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
def price_quote_consumer(
    consumer_obj: mock.AsyncMock,
    producer_obj: mock.AsyncMock,
    redis_client: aioredis.Redis[bytes],
    ba_ndc_client: client.BaNdcClient,
    airport_repository: airports.AirportRepository,
) -> pricing.PriceQuoteConsumer:
    return pricing.PriceQuoteConsumer(
        consumer_obj=consumer_obj,
        producer_obj=producer_obj,
        offer_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
        price_quote_cache=cache.PriceQuoteCache(
            client=redis.Client(redis_client),
        ),
        price_ttl=datetime.timedelta(minutes=45),
        provider_company_id="provider_company_id",
        ba_ndc_client=ba_ndc_client,
        airport_repository=airport_repository,
    )


@pytest.fixture()
async def get_offer_response() -> Any:
    return await load_file_fixture("get_offer_response.json")


@pytest.fixture()
async def mock_get_offer(
    get_offer_response: response_priced_offer_schemas.PricedOfferResponse,
) -> AsyncGenerator[response_priced_offer_schemas.PricedOfferResponse, None]:
    parsed_offer = response_priced_offer_schemas.PricedOfferResponse.parse_raw(
        json.dumps(get_offer_response),
    )

    with mock.patch(
        "snowfall.vendor.ba_ndc.client.BaNdcClient.get_offer",
    ) as mock_get_offer:
        mock_get_offer.return_value = parsed_offer
        yield mock_get_offer
