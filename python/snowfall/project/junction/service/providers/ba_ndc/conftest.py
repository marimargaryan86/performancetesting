from __future__ import annotations

import datetime
import uuid
from typing import Any, cast

import httpx
import pytest
from bson import json_util
from redis import asyncio as aioredis

from snowfall.project.junction.provider import airports
from snowfall.project.junction.service.providers.ba_ndc import cache
from snowfall.project.junction.service.providers.ba_ndc.search import adapter
from snowfall.project.junction.service.providers.ba_ndc.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.ba_ndc import client
from snowfall.vendor.ba_ndc.adapters.offers_response_adapter import (
    OffersResponseAdapter,
)

_TIMEOUT = 50.0
API_BASE_URL = "https://ndc.junction.travel"


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=_TIMEOUT)


@pytest.fixture
def ba_ndc_client(http_client: httpx.AsyncClient) -> client.BaNdcClient:
    return client.BaNdcClient(
        api_base_url=API_BASE_URL,
        api_key="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJyZXRhaWxlcl9pZCI6MTIzLCJleHBpcmVzIjoxNjk0MTU0MjM3Ljk5MDIxNDh9.c_5YzFgzL_myYg9UT8cTYxz32mVR0ZLQZV9h0XueH-A",
        http_client=http_client,
    )


@pytest.fixture
async def airport_repository() -> airports.AirportRepository:
    loader = filesystem.PkgLoader(__name__)

    return airports.AirportRepository(
        cast(list[dict[str, Any]], loader.load("airports.json")),
    )


@pytest.fixture
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
                        tzinfo=datetime.timezone.utc,
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


def load_file_fixture(
    file_name: str,
) -> Any:
    file_path = filesystem.resource_path(
        package=__name__,
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    with open(file_path) as json_file:
        return json_util.loads(json_file.read())
