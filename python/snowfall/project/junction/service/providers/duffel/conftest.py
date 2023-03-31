from __future__ import annotations

import datetime
import uuid
import zoneinfo
from typing import Any

import httpx
import pytest
from bson import json_util
from redis import asyncio as aioredis

from snowfall.project.junction.service.providers.duffel import cache
from snowfall.project.junction.service.providers.duffel.search import adapter, parser
from snowfall.project.junction.service.providers.duffel.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.models.offer import Offer

API_BASE_URL = "https://api.duffel.com"
_TIMEOUT = 50.0
_TTL_MINUTES = 15
_PASSENGER_AGE = 30


@pytest.fixture()
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=_TIMEOUT)


@pytest.fixture()
def duffel_client(http_client: httpx.AsyncClient) -> client.DuffelClient:
    return client.DuffelClient(
        api_base_url=API_BASE_URL,
        api_key="duffel_test_mwCE9C8Ai452UaenWhexo9PQuz1VWbmzzU9ejcVDy3p",
        version="v1",
        http_client=http_client,
    )


@pytest.fixture()
def search_adapter(
    duffel_client: client.DuffelClient,
    redis_client: aioredis.Redis[bytes],
) -> adapter.DuffelSearchAdapter:
    return adapter.DuffelSearchAdapter(
        duffel_client=duffel_client,
        offers_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
        ttl=datetime.timedelta(minutes=_TTL_MINUTES),
    )


@pytest.fixture()
def search_adapter_no_ba(
    duffel_client: client.DuffelClient,
    redis_client: aioredis.Redis[bytes],
) -> adapter.DuffelSearchAdapter:
    return adapter.DuffelSearchAdapter(
        duffel_client=duffel_client,
        offers_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
        ttl=datetime.timedelta(minutes=_TTL_MINUTES),
        disabled_airlines={"BA"},
    )


@pytest.fixture()
def search_adapter_ba_only(
    duffel_client: client.DuffelClient,
    redis_client: aioredis.Redis[bytes],
) -> adapter.DuffelSearchAdapter:
    return adapter.DuffelSearchAdapter(
        duffel_client=duffel_client,
        offers_cache=cache.OfferCache(
            client=redis.Client(redis_client),
        ),
        ttl=datetime.timedelta(minutes=_TTL_MINUTES),
        enabled_airlines={"BA"},
    )


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
                            coordinates=models_pb2.Coordinates(
                                longitude=offer_leg.origin.longitude,
                                latitude=offer_leg.origin.latitude,
                            ),
                            time_zone=offer_leg.origin.time_zone,
                        ),
                        destination=models_pb2.Point(
                            coordinates=models_pb2.Coordinates(
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
