import asyncio
import datetime
import types as std_types
from collections.abc import AsyncIterable, AsyncIterator, Callable
from typing import Generic, Self, TypeVar

import prometheus_client
from google.protobuf import message

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.v1 import amqp_pb2 as stdlib_amqp_pb2

_Proto = TypeVar("_Proto", bound=message.Message)
TripOfferSearchMessages = (
    offers_amqp_pb2.TripOfferSearchTask | stdlib_amqp_pb2.Trackable
)
TripOfferSearchCriteriaGenerator = Callable[
    [offers_amqp_pb2.TripOfferSearchTask],
    list[_Proto],
]
_CriteriaType = TypeVar("_CriteriaType")
CacheKeyGenerator = Callable[[_CriteriaType], str]
OfferGroupGenerator = Callable[
    [_CriteriaType],
    AsyncIterator[offers_pb2.OfferGroup],
]
# This timeout is just a safety mechanism (in case the lock doesn't get
# released). In reality, it should never occur.
_CACHE_LOCK_TTL_SECONDS = 180


class NoCacheExistsError(Exception):
    """Thrown when the cache for an offer search hasn't been created yet."""


class OfferGroupCache(object):
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
        self._offers = redis.set_("criteria_cache.offers:{0}".format(cache_key))
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

    async def to_iterable(self) -> AsyncIterable[offers_pb2.OfferGroup]:
        if not await self._redis.get(self._seen_key):
            raise NoCacheExistsError

        async for offer in self._offers.to_iterable():
            yield offers_pb2.OfferGroup.FromString(offer)

    async def put(
        self,
        offer: offers_pb2.OfferGroup,
    ) -> None:
        await self._offers.add(offer.SerializeToString(deterministic=True))
        await redis_types.put_expires_at_if_less_than_current(
            self._redis,
            self._offers,
            offer.expires_at.ToDatetime(tzinfo=datetime.UTC),
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
            await self._redis.get_expires_at(self._offers) or fallback_expiry,
        )


class OfferGroupRepository(Generic[_CriteriaType]):
    _counter_requests = prometheus_client.Counter(
        "provider_offers",
        "The total ratio of cache hits.",
        labelnames=("cached",),
    )

    def __init__(
        self,
        offer_group_cache_key_func: CacheKeyGenerator[_CriteriaType],
        redis: redis_types.Client[bytes],
        offer_group_generator: OfferGroupGenerator[_CriteriaType],
    ) -> None:
        self._offer_group_cache_key_func = offer_group_cache_key_func
        self._redis = redis
        self._offer_group_generator = offer_group_generator

    async def find(
        self,
        search_criteria: _CriteriaType,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        offer_cache = OfferGroupCache(
            self._offer_group_cache_key_func(search_criteria),
            self._redis,
        )

        async with offer_cache:
            search_offers = self._search_offers(search_criteria, offer_cache)
            async for cached_offer_group in search_offers:
                yield cached_offer_group

    async def _search_offers(
        self,
        search_criteria: _CriteriaType,
        offer_cache: OfferGroupCache,
    ) -> AsyncIterable[offers_pb2.OfferGroup]:
        try:
            async for cached_offer_group in offer_cache.to_iterable():
                self._counter_requests.labels(
                    cached=True,
                ).inc()

                yield cached_offer_group

        except NoCacheExistsError:
            # Shield to ensure it writes to offer cache even if we timeout.
            offers = await asyncio.shield(
                self._create_offers(search_criteria, offer_cache),
            )
            for offer in offers:
                yield offer

    async def _create_offers(
        self,
        search_criteria: _CriteriaType,
        offer_cache: OfferGroupCache,
    ) -> list[offers_pb2.OfferGroup]:
        offer_results = []
        async for offer_result in self._offer_group_generator(search_criteria):
            await offer_cache.put(offer_result)
            self._counter_requests.labels(cached=False).inc()

            offer_results.append(offer_result)

        await offer_cache.mark_as_seen()

        return offer_results
