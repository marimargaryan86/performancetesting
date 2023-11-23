from __future__ import annotations

import datetime
import typing
import uuid
import zoneinfo
from collections.abc import AsyncIterator
from unittest import mock

import aiofiles
import httpx
import orjson
import pytest
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.service.providers.duffel import (
    cache,
    client_factory,
    pricing,
    pricing_adapter,
    pricing_transformer,
)
from snowfall.project.junction.service.providers.duffel.search import adapter, parser
from snowfall.project.junction.service.providers.duffel.v1 import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.models.offer import Offer
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

API_BASE_URL = "https://api.duffel.com"
_TIMEOUT = 50.0
_TTL_MINUTES = 15
_PASSENGER_AGE = 30


@pytest.fixture()
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=_TIMEOUT)


@pytest.fixture()
def resellers_map() -> typing.Mapping[str, typing.Any]:
    return {
        "res1": {
            "api_key": "token1",
            "private_fares": {
                "QF": [
                    {
                        "tracking_reference": "ABN:2345678",
                        "corporate_code": "FLX53",
                    },
                ],
            },
        },
    }


@pytest.fixture()
def duffel_client_factory(
    http_client: httpx.AsyncClient,
    resellers_map: typing.Mapping[str, typing.Any],
) -> client_factory.DuffelClientFactory:
    mock_rate_limit_client = mock.create_autospec(
        RateLimitClient,
        spec_set=True,
        instance=True,
    )
    return client_factory.DuffelClientFactory(
        api_base_url=API_BASE_URL,
        api_key="duffel_test_mwCE9C8Ai452UaenWhexo9PQuz1VWbmzzU9ejcVDy3p",
        version="v1",
        http_client=http_client,
        resellers_map=resellers_map,
        rate_limit_client=mock_rate_limit_client,
    )


@pytest.fixture()
def duffel_client(http_client: httpx.AsyncClient) -> client.DuffelClient:
    mock_rate_limit_client = mock.create_autospec(
        RateLimitClient,
        spec_set=True,
        instance=True,
    )
    return client.DuffelClient(
        api_base_url=API_BASE_URL,
        api_key="duffel_test_mwCE9C8Ai452UaenWhexo9PQuz1VWbmzzU9ejcVDy3p",
        version="v1",
        http_client=http_client,
        rate_limit_client=mock_rate_limit_client,
    )


@pytest.fixture()
def search_adapter(
    redis_client: aioredis.Redis[bytes],
    duffel_client_factory: client_factory.DuffelClientFactory,
    resellers_map: typing.Mapping[str, typing.Any],
) -> adapter.DuffelSearchAdapter:
    return adapter.DuffelSearchAdapter(
        duffel_client_factory=duffel_client_factory,
        offers_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
        ttl=datetime.timedelta(minutes=_TTL_MINUTES),
        resellers_map=resellers_map,
    )


@pytest.fixture()
def search_adapter_no_ba(
    redis_client: aioredis.Redis[bytes],
    duffel_client_factory: client_factory.DuffelClientFactory,
    resellers_map: typing.Mapping[str, typing.Any],
) -> adapter.DuffelSearchAdapter:
    return adapter.DuffelSearchAdapter(
        duffel_client_factory=duffel_client_factory,
        offers_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
        ttl=datetime.timedelta(minutes=_TTL_MINUTES),
        disabled_airlines=frozenset(("BA",)),
        resellers_map=resellers_map,
    )


@pytest.fixture()
def search_adapter_ba_only(
    duffel_client: client.DuffelClient,
    redis_client: aioredis.Redis[bytes],
    duffel_client_factory: client_factory.DuffelClientFactory,
    resellers_map: typing.Mapping[str, typing.Any],
) -> adapter.DuffelSearchAdapter:
    return adapter.DuffelSearchAdapter(
        duffel_client_factory=duffel_client_factory,
        offers_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
        ttl=datetime.timedelta(minutes=_TTL_MINUTES),
        enabled_airlines=frozenset(("BA",)),
        resellers_map=resellers_map,
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
    return datetime.timedelta(minutes=1)


@pytest.fixture()
def provider_company_id() -> str:
    return "provider_id"


@pytest.fixture()
def offer_cache() -> cache.OfferCache:
    return cache.OfferCache(client=redis.Client(aioredis.Redis()))


@pytest.fixture()
def passenger() -> cache.OfferDetailsPassenger:
    return cache.OfferDetailsPassenger(
        identifier="test_passenger_id",
        passenger_type="adult",
    )


@pytest.fixture()
def offer_details(passenger: cache.OfferDetailsPassenger) -> cache.OfferDetails:
    return cache.OfferDetails(
        offer_id="test_offer_id",
        passengers=[passenger],
        total_amount="100.00",
        currency="EUR",
        doc_required=False,
        last_travel_date=datetime.datetime.now(tz=datetime.UTC),
    )


@pytest.fixture()
def adapter_factory() -> mock.AsyncMock:
    factory = mock.create_autospec(pricing_adapter.PricingAdapterFactory)
    return factory.return_value


@pytest.fixture()
def price_quote_consumer(
    consumer_obj: mock.AsyncMock,
    producer_obj: mock.AsyncMock,
    offer_ttl: datetime.timedelta,
    redis_client: aioredis.Redis[bytes],
    provider_company_id: str,
    resellers_map: typing.Mapping[str, typing.Any],
    duffel_client_factory: client_factory.DuffelClientFactory,
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
        offer_ttl=offer_ttl,
        provider_company_id=provider_company_id,
        adapter_factory=pricing_adapter.PricingAdapterFactory(duffel_client_factory),
        transformer=pricing_transformer.PriceQuoteTransformer(
            offer_cache=cache.OfferCache(
                client=redis.Client(redis_client),
            ),
        ),
        resellers_map=resellers_map,
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


def search_task_from_offer(offer: Offer) -> amqp_pb2.SearchCriteriaTask:
    first_segment = offer.slices[0].segments[0]
    last_segment = offer.slices[0].segments[-1]

    return amqp_pb2.SearchCriteriaTask(
        offer_search_id=str(uuid.uuid4()),
        segments=[
            models_pb2.Segment(
                id=str(uuid.uuid4()),
                legs=[
                    models_pb2.Leg(
                        id=str(uuid.uuid4()),
                        origin=models_pb2.Point(
                            coordinates=latlng_pb2.LatLng(
                                longitude=offer_leg.origin.longitude,
                                latitude=offer_leg.origin.latitude,
                            ),
                            time_zone=offer_leg.origin.time_zone,
                        ),
                        destination=models_pb2.Point(
                            coordinates=latlng_pb2.LatLng(
                                longitude=offer_leg.destination.longitude,
                                latitude=offer_leg.destination.latitude,
                            ),
                            time_zone=offer_leg.destination.time_zone,
                        ),
                        departure_at=protobuf.datetime_to_protobuf(
                            offer_leg.departing_at.replace(
                                tzinfo=zoneinfo.ZoneInfo(
                                    offer_leg.origin.time_zone,
                                ),
                            ),
                        ),
                        arrival_at=protobuf.datetime_to_protobuf(
                            offer_leg.arriving_at.replace(
                                tzinfo=zoneinfo.ZoneInfo(
                                    offer_leg.destination.time_zone,
                                ),
                            ),
                        ),
                        type=models_pb2.Schedule.Type.TYPE_AIR,
                    )
                    for offer_leg in parser.segment_to_legs(offer_segment)
                ],
            )
            for offer_slice in offer.slices
            for offer_segment in offer_slice.segments
        ],
        criteria=amqp_pb2.Criteria(
            origin_iata=first_segment.origin.iata_code or "",
            destination_iata=last_segment.destination.iata_code or "",
            outbound_departure=protobuf.datetime_to_protobuf_datetime(
                first_segment.departing_at.replace(
                    tzinfo=zoneinfo.ZoneInfo(
                        first_segment.origin.time_zone,
                    ),
                ),
            ),
            passenger_ages=[_PASSENGER_AGE],
        ),
        session_token=str(uuid.uuid4()),
    )


async def load_file_fixture(
    file_name: str,
) -> typing.Any:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.duffel.client",
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    async with aiofiles.open(file_path) as json_file:
        return orjson.loads(await json_file.read())
