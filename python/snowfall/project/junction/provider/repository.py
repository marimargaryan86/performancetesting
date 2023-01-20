import datetime
import types as std_types
from typing import AsyncIterable, AsyncIterator, Callable, Type, TypeVar

from google.protobuf import message

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1alpha import amqp_pb2 as stdlib_amqp_pb2

_Proto = TypeVar("_Proto", bound=message.Message)
TripOfferSearchMessages = (
    offers_amqp_pb2.TripOfferSearchTask | stdlib_amqp_pb2.Trackable
)
TripOfferSearchCriteriaGenerator = Callable[
    [offers_amqp_pb2.TripOfferSearchTask],
    list[_Proto],
]


class NoCacheExistsError(Exception):
    """Thrown when the cache for an offer search hasn't been created yet."""


class OfferGroupCache(object):
    _blocking_timeout = datetime.timedelta(seconds=10)  # todo: tweak to what we want
    _lock_timeout = datetime.timedelta(minutes=5)  # todo: tweak to what we want

    def __init__(
        self,
        cache_key: str,
        redis: redis_types.Client[bytes],
    ) -> None:
        self._seen_key = "criteria_cache.seen:{0}".format(cache_key)
        self._lock = redis.lock(
            name="criteria_cache.locks:{0}".format(cache_key),
            timeout=self._lock_timeout.total_seconds(),
            blocking_timeout=self._blocking_timeout.total_seconds(),
        )
        self._offers = redis.set_("criteria_cache.offers:{0}".format(cache_key))
        self._redis = redis

    async def __aenter__(self) -> bool:
        return await self._lock.acquire()

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: std_types.TracebackType | None,
    ) -> bool:
        # only claim to have cached results if we were successful
        if not exc_type:
            fallback_expiry = datetime.datetime.now(
                tz=datetime.timezone.utc,
            ) + datetime.timedelta(
                hours=1,
            )  # todo: tweak to what we want

            await self._redis.put(self._seen_key, b"\x00")
            await redis_types.put_expires_at_if_less_than_current(
                self._redis,
                self._seen_key,
                await self._redis.get_expires_at(self._offers) or fallback_expiry,
            )

        if await self._lock.owned():
            await self._lock.release()

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
            offer.expires_at.ToDatetime(tzinfo=datetime.timezone.utc),
        )


class OfferGroupRepository(object):
    def __init__(
        self,
        offer_group_cache_key_func: Callable[[_Proto], str],
        redis: redis_types.Client[bytes],
        offer_group_generator: Callable[[_Proto], AsyncIterator[offers_pb2.OfferGroup]],
    ) -> None:
        self._offer_group_cache_key_func = offer_group_cache_key_func
        self._redis = redis
        self._offer_group_generator = offer_group_generator

    async def find(
        self,
        amqp_message: amqp_types.Message[_Proto],
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        offer_cache = OfferGroupCache(
            self._offer_group_cache_key_func(amqp_message.body),
            self._redis,
        )

        async with offer_cache as has_lock:
            if has_lock:
                async for cached_offer_group in self._search_offers(  # noqa: WPS352
                    amqp_message.body,
                    offer_cache,
                ):
                    yield cached_offer_group
            else:
                await amqp_message.nack(requeue=True)

    async def _search_offers(
        self,
        search_task: _Proto,
        offer_cache: OfferGroupCache,
    ) -> AsyncIterable[offers_pb2.OfferGroup]:
        try:
            async for cached_offer_group in offer_cache.to_iterable():
                yield cached_offer_group

        except NoCacheExistsError:
            async for offer_result in self._offer_group_generator(search_task):
                await offer_cache.put(offer_result)
                yield offer_result
