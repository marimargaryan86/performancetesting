import asyncio
import datetime
import types as std_types
from collections.abc import AsyncIterable, AsyncIterator, Callable
from typing import Generic, Self, TypeVar

import prometheus_client
from google.protobuf import message

from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.v1 import amqp_pb2 as stdlib_amqp_pb2

_Proto = TypeVar("_Proto", bound=message.Message)
SearchMessages = amqp_pb2.SearchTask | stdlib_amqp_pb2.Trackable
SearchCriteriaGenerator = Callable[[amqp_pb2.SearchTask], list[_Proto]]
_CriteriaType = TypeVar("_CriteriaType")
CacheKeyGenerator = Callable[[_CriteriaType], str]
SearchResultGenerator = Callable[
    [_CriteriaType],
    AsyncIterator[models_pb2.SearchResult],
]
# This timeout is just a safety mechanism (in case the lock doesn't get
# released). In reality, it should never occur.
_CACHE_LOCK_TTL_SECONDS = 180


class NoCacheExistsError(Exception):
    """Thrown when the cache for a search hasn't been created yet."""


class SearchResultCache(object):
    def __init__(
        self,
        cache_key: str,
        redis: redis_types.Client[bytes],
    ) -> None:
        self._seen_key = "criteria_cache.seen:{0}".format(cache_key)
        self._lock = redis.lock(
            "criteria_cache.locks:{0}".format(cache_key),
            timeout=_CACHE_LOCK_TTL_SECONDS,
        )
        self._search_results = redis.set_(
            "criteria_cache.search_results:{0}".format(cache_key),
        )
        self._redis = redis

    async def __aenter__(self) -> Self:
        await self._lock.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: std_types.TracebackType | None,
    ) -> bool:
        await self._lock.__aexit__(exc_type, exc_value, traceback)

        return False

    async def to_iterable(self) -> AsyncIterable[models_pb2.SearchResult]:
        if not await self._redis.get(self._seen_key):
            raise NoCacheExistsError

        async for search_result in self._search_results.to_iterable():
            yield models_pb2.SearchResult.FromString(search_result)

    async def put(
        self,
        search_result: models_pb2.SearchResult,
    ) -> None:
        await self._search_results.add(
            search_result.SerializeToString(deterministic=True),
        )
        await redis_types.put_expires_at_if_less_than_current(
            self._redis,
            self._search_results,
            search_result.expires_at.ToDatetime(tzinfo=datetime.UTC),
        )

    async def mark_as_seen(self) -> None:
        fallback_expiry = datetime.datetime.now(
            tz=datetime.UTC,
        ) + datetime.timedelta(
            hours=1,
        )  # TODO(jyggen): tweak to what we want

        await self._redis.put(self._seen_key, b"\x00")
        await redis_types.put_expires_at_if_less_than_current(
            self._redis,
            self._seen_key,
            await self._redis.get_expires_at(self._search_results) or fallback_expiry,
        )


class SearchResultRepository(Generic[_CriteriaType]):
    _counter_requests = prometheus_client.Counter(
        "provider_search_results",
        "The total ratio of cache hits.",
        labelnames=("cached",),
    )

    def __init__(
        self,
        search_result_cache_key_func: CacheKeyGenerator[_CriteriaType],
        redis: redis_types.Client[bytes],
        search_result_generator: SearchResultGenerator[_CriteriaType],
    ) -> None:
        self._search_result_cache_key_func = search_result_cache_key_func
        self._redis = redis
        self._search_result_generator = search_result_generator

    async def find(
        self,
        search_criteria: _CriteriaType,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        search_result_cache = SearchResultCache(
            self._search_result_cache_key_func(search_criteria),
            self._redis,
        )

        async with search_result_cache:
            search_results = self._search_results(search_criteria, search_result_cache)
            async for cached_search_result in search_results:
                yield cached_search_result

    async def _search_results(
        self,
        search_criteria: _CriteriaType,
        search_result_cache: SearchResultCache,
    ) -> AsyncIterable[models_pb2.SearchResult]:
        try:
            async for cached_search_result in search_result_cache.to_iterable():
                self._counter_requests.labels(
                    cached=True,
                ).inc()

                yield cached_search_result

        except NoCacheExistsError:
            # Shield to ensure it writes to search cache even if we timeout.
            search_results = await asyncio.shield(
                self._create_search_results(search_criteria, search_result_cache),
            )
            for search_result in search_results:
                yield search_result

    async def _create_search_results(
        self,
        search_criteria: _CriteriaType,
        search_result_cache: SearchResultCache,
    ) -> list[models_pb2.SearchResult]:
        search_results = []
        async for search_result in self._search_result_generator(search_criteria):
            await search_result_cache.put(search_result)
            self._counter_requests.labels(cached=False).inc()

            search_results.append(search_result)

        await search_result_cache.mark_as_seen()

        return search_results
