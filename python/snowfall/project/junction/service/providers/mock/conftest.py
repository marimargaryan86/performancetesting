from __future__ import annotations

import contextlib
import datetime
from typing import AsyncIterator
from unittest import mock

import more_itertools
import pytest
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1alpha import models_pb2 as common_pb2
from snowfall.project.junction.provider import offers as provider_offers
from snowfall.project.junction.provider import service
from snowfall.project.junction.service.providers.mock import main, offers
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import types


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
                                    datetime.datetime.now(),
                                ),
                                arrival_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
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
async def searcher(
    redis_client: aioredis.Redis[bytes],
) -> provider_offers.TripOfferSearcher[offers.Criteria, offers.Criteria]:
    wrapped_redis_client = redis.Client[bytes](redis_client, prefix="foo")
    implementation = await main._offers_search(  # noqa: WPS437
        app=mock.create_autospec(service.Application),
        amqp_conn=mock.create_autospec(types.Connection),
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
