from __future__ import annotations

import datetime
import hashlib
from typing import NamedTuple

from redis.asyncio import lock as aiolock

from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.project.junction.service.gateway import providers
from snowfall.stdlib.persistence.redis import types


class Factory(object):
    def __init__(
        self,
        client: types.Client[bytes],
        ttl: datetime.timedelta,
    ) -> None:
        self._client = client
        self._ttl = ttl

    def create(
        self,
        provider: providers.Provider,
        request: provider_trips_pb2.SearchTripsRequest,
    ) -> Store:
        keys = _generate_keys(provider, request)

        return Store(
            client=self._client,
            keys=keys,
            ttl=self._ttl,
        )


class Store(object):
    def __init__(
        self,
        client: types.Client[bytes],
        keys: _Keys,
        ttl: datetime.timedelta,
    ):
        self._client = client
        self._keys = keys
        self._ttl = ttl

    async def get(self) -> provider_trips_pb2.SearchTripsResponse | None:
        cached_data = await self._client.get(self._keys.results)

        if cached_data is None:
            return None

        response = provider_trips_pb2.SearchTripsResponse()
        response.ParseFromString(cached_data)

        return response

    def lock(self) -> aiolock.Lock:
        # TODO(jyggen): set proper timeouts
        return self._client.lock(self._keys.lock)

    async def put(self, response: provider_trips_pb2.SearchTripsResponse) -> None:
        await self._client.put(
            self._keys.results,
            response.SerializeToString(),
            expiry=datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )


class _Keys(NamedTuple):
    lock: str
    results: str


def _generate_keys(
    provider: providers.Provider,
    request: provider_trips_pb2.SearchTripsRequest,
) -> _Keys:
    request_key = hashlib.sha384(
        request.SerializeToString(deterministic=True),
    ).hexdigest()

    return _Keys(
        lock="trips.cache.{0}.{1}.lock".format(provider.identifier, request_key),
        results="trips.cache.{0}.{1}.results".format(provider.identifier, request_key),
    )
