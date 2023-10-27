from __future__ import annotations

import datetime

import freezegun
import pytest
from grpc import aio
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.gateway import providers
from snowfall.project.junction.go.service.gateway.trips import cache
from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.stdlib.persistence.redis import types

_FREEZE_TIME_AT = datetime.datetime(year=2023, month=10, day=25, tzinfo=datetime.UTC)
_FOO_BAR_REQUEST = provider_trips_pb2.SearchTripsRequest(
    one_way=provider_trips_pb2.SearchTripsRequest.OneWay(
        criterion=provider_trips_pb2.SearchTripsRequest.Criterion(
            origin_identifier="FOO",
            destination_identifier="BAR",
        ),
    ),
)

_BAZ_QUX_REQUEST = provider_trips_pb2.SearchTripsRequest(
    one_way=provider_trips_pb2.SearchTripsRequest.OneWay(
        criterion=provider_trips_pb2.SearchTripsRequest.Criterion(
            origin_identifier="BAZ",
            destination_identifier="QUX",
        ),
    ),
)

_FOO_PROVIDER = providers.Provider(
    connection=providers.Connection(aio.insecure_channel("foobar")),
    identifier="foo",
)

_BAR_PROVIDER = providers.Provider(
    connection=providers.Connection(aio.insecure_channel("foobar")),
    identifier="bar",
)


@pytest.fixture()
def one_second_ttl_cache_factory(redis_client: aioredis.Redis[bytes]) -> cache.Factory:
    return cache.Factory(
        client=types.Client(redis_client),
        ttl=datetime.timedelta(seconds=1),
    )


@freezegun.freeze_time(time_to_freeze=_FREEZE_TIME_AT)
async def test_cache_supports_different_providers(
    one_second_ttl_cache_factory: cache.Factory,
) -> None:
    store1 = one_second_ttl_cache_factory.create(_FOO_PROVIDER, _FOO_BAR_REQUEST)
    store2 = one_second_ttl_cache_factory.create(_BAR_PROVIDER, _FOO_BAR_REQUEST)

    await store1.put(
        response=provider_trips_pb2.SearchTripsResponse(
            results=[
                provider_trips_pb2.Result(),
            ],
        ),
    )

    assert await store1.get()
    assert not await store2.get()


@freezegun.freeze_time(time_to_freeze=_FREEZE_TIME_AT)
async def test_cache_supports_different_requests(
    one_second_ttl_cache_factory: cache.Factory,
) -> None:
    store1 = one_second_ttl_cache_factory.create(_FOO_PROVIDER, _FOO_BAR_REQUEST)
    store2 = one_second_ttl_cache_factory.create(_FOO_PROVIDER, _BAZ_QUX_REQUEST)

    await store1.put(
        response=provider_trips_pb2.SearchTripsResponse(
            results=[
                provider_trips_pb2.Result(),
            ],
        ),
    )

    assert await store1.get()
    assert not await store2.get()


async def test_cache_is_respecting_ttl(
    one_second_ttl_cache_factory: cache.Factory,
) -> None:
    store = one_second_ttl_cache_factory.create(_FOO_PROVIDER, _FOO_BAR_REQUEST)

    with freezegun.freeze_time(time_to_freeze=_FREEZE_TIME_AT) as frozen_datetime:
        await store.put(
            response=provider_trips_pb2.SearchTripsResponse(
                results=[
                    provider_trips_pb2.Result(),
                ],
            ),
        )

        assert await store.get()
        frozen_datetime.tick(datetime.timedelta(seconds=2))
        assert not await store.get()


async def test_cache_is_caching_empty_results(
    one_second_ttl_cache_factory: cache.Factory,
) -> None:
    store = one_second_ttl_cache_factory.create(_FOO_PROVIDER, _FOO_BAR_REQUEST)

    await store.put(response=provider_trips_pb2.SearchTripsResponse(results=[]))
    assert await store.get()
