from __future__ import annotations

import contextlib
import datetime
import uuid
from collections.abc import AsyncIterator
from unittest import mock

import aio_pika
import faker
import more_itertools
import pytest
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.provider import offers as provider_offers
from snowfall.project.junction.provider import service
from snowfall.project.junction.service.providers.mock import (
    bookings,
    cache,
    main,
    offers,
    pricing,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis


def generate_offer_search(
    trips: int = 1,
    segments: int = 1,
    legs: int = 1,
) -> offers_pb2.TripOfferSearch:
    return offers_pb2.TripOfferSearch(
        trips=[
            common_pb2.Trip(
                segments=[
                    common_pb2.Segment(
                        id=string.uuid(),
                        legs=[
                            common_pb2.Leg(
                                origin=common_pb2.Point(
                                    time_zone="UTC",
                                ),
                                destination=common_pb2.Point(
                                    time_zone="UTC",
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(tz=datetime.UTC),
                                ),
                                arrival_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(tz=datetime.UTC),
                                ),
                                type=common_pb2.Schedule.TYPE_AIR,
                            )
                            for _ in range(legs)
                        ],
                    )
                    for _ in range(segments)
                ],
            )
            for _ in range(trips)
        ],
    )


@pytest.fixture()
def fake() -> faker.Faker:
    return faker.Faker()


@pytest.fixture()
async def searcher(
    redis_client: aioredis.Redis[bytes],
) -> provider_offers.TripOfferSearcher[offers.Criteria, offers.Criteria]:
    wrapped_redis_client = redis.Client[bytes](redis_client, prefix="foo")
    app = mock.create_autospec(service.Application)
    app.name = "mock"
    app.settings = mock.create_autospec(main._Settings)  # noqa: SLF001
    app.settings.realistic_results = False
    app.settings.ttl = datetime.timedelta(minutes=1)
    implementation = await main._offers_factory(  # noqa: SLF001
        app=app,
        amqp_conn=mock.create_autospec(aio_pika.Connection),
        redis_conn=redis_client,
        stack=mock.create_autospec(contextlib.AsyncExitStack),
    )

    return provider_offers.TripOfferSearcher.from_implementation(
        implementation=implementation,
        redis_client=wrapped_redis_client,
    )


@pytest.fixture()
def simple_offer_search() -> offers_pb2.TripOfferSearch:
    return generate_offer_search()


@pytest.fixture()
async def offer_group(
    searcher: provider_offers.TripOfferSearcher[offers.Criteria, offers.Criteria],
    simple_offer_search: offers_pb2.TripOfferSearch,
) -> AsyncIterator[offers_pb2.OfferGroup]:
    async for offer_group in searcher.search(simple_offer_search):
        yield offer_group


@pytest.fixture()
def offer_segment(offer_group: offers_pb2.OfferGroup) -> offers_pb2.OfferSegment:
    return more_itertools.first(offer_group.segments)


@pytest.fixture()
def search_segment(
    simple_offer_search: offers_pb2.TripOfferSearch,
) -> common_pb2.Segment:
    first_trip = more_itertools.first(simple_offer_search.trips)

    return more_itertools.first(first_trip.segments)


@pytest.fixture()
def offer_segment_leg(
    offer_segment: offers_pb2.OfferSegment,
) -> offers_pb2.OfferSegmentLeg:
    return more_itertools.first(offer_segment.legs)


@pytest.fixture()
def search_leg(search_segment: common_pb2.Segment) -> common_pb2.Leg:
    return more_itertools.first(search_segment.legs)


@pytest.fixture()
def offer_option(offer_group: offers_pb2.OfferGroup) -> offers_pb2.Offer:
    return more_itertools.first(offer_group.offers)


@pytest.fixture()
def offer_segment_details(
    offer_option: offers_pb2.Offer,
) -> offers_pb2.OfferSegmentDetails:
    return more_itertools.first(offer_option.segment_details)


@pytest.fixture()
def option_cache(redis_client: aioredis.Redis[bytes]) -> cache.OptionCache:
    return cache.OptionCache(client=redis.Client(redis_client))


@pytest.fixture()
def price_quote_cache(redis_client: aioredis.Redis[bytes]) -> cache.PriceQuoteCache:
    return cache.PriceQuoteCache(client=redis.Client(redis_client))


@pytest.fixture()
def quoter(
    option_cache: cache.OptionCache,
    price_quote_cache: cache.PriceQuoteCache,
) -> pricing.Quoter:
    return pricing.Quoter(
        option_cache=option_cache,
        price_quote_cache=price_quote_cache,
        ttl=datetime.timedelta(minutes=1),
    )


@pytest.fixture()
def price(fake: faker.Faker) -> money.Money:
    return money.from_string(
        string_amount=fake.numerify(text="%#"),
        currency=money.Currency("EUR"),
    )


@pytest.fixture()
async def option_id(option_cache: cache.OptionCache, price: money.Money) -> str:
    return await option_cache.store(
        cache.MockDetails(
            amount=price.amount,
            currency=price.currency.code,
        ),
    )


@pytest.fixture()
async def price_quote(
    option_id: str,
    quoter: pricing.Quoter,
) -> offers_pb2.PriceQuote:
    return await quoter.generate_quote(option_id)


@pytest.fixture()
async def storage() -> AsyncIterator[filesystem.Storage]:
    async with filesystem.Storage.from_dsn("memory://") as storage_obj:
        yield storage_obj


@pytest.fixture()
def booker(
    price_quote_cache: cache.PriceQuoteCache,
    storage: filesystem.Storage,
) -> bookings.Booker:
    return bookings.Booker(
        price_quote_cache=price_quote_cache,
        booking_storage=storage,
        provider_id=uuid.uuid4(),
        provider_name="Mock",
    )
