import contextlib
import datetime
import types as std_types
from typing import AsyncIterable, Type

from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class OfferDetails(RedisRecord):
    pricing_id: str
    transaction_id: str


class OfferCache(RedisRepository[OfferDetails]):
    """Stores offer details in the cache."""

    _record_type: Type[OfferDetails] = OfferDetails


class NoCacheExistsError(Exception):
    """Thrown when the cache for an offer search hasn't been created yet."""


class OfferGroupCache(contextlib.AsyncContextDecorator):
    _lock_timeout_seconds = 120  # todo: tweak to what we want

    def __init__(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        redis: types.Client[bytes],
    ) -> None:
        cache_key = string.to_uuid(
            b"\x00".decode().join(
                sorted(
                    [
                        search_task.session_token,
                        *[segment.id for segment in search_task.segments],
                    ],
                ),
            ),
        )

        self._seen_key = "criteria_cache.seen:{0}".format(cache_key)
        self._lock = redis.lock(
            name="criteria_cache.locks:{0}".format(cache_key),
            timeout=self._lock_timeout_seconds,
        )
        self._offers = redis.set_("criteria_cache.offers:{0}".format(cache_key))
        self._redis = redis

    async def __aenter__(self) -> "OfferGroupCache":
        await self._lock.acquire()

        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: std_types.TracebackType | None,
    ) -> bool:
        fallback_expiry = datetime.datetime.now(
            tz=datetime.timezone.utc,
        ) + datetime.timedelta(
            hours=1,
        )  # todo: tweak to what we want

        await self._redis.put(self._seen_key, b"\x00")
        await types.put_expires_at_if_less_than_current(
            self._redis,
            self._seen_key,
            await self._redis.get_expires_at(self._offers) or fallback_expiry,
        )

        await self._lock.release()

        return False  # type: ignore[unreachable]

    async def to_iterable(self) -> AsyncIterable[offers_pb2.OfferGroup]:
        if not self._redis.get(self._seen_key):
            raise NoCacheExistsError

        async for offer in self._offers.to_iterable():
            yield offers_pb2.OfferGroup.FromString(offer)

    async def put(
        self,
        offer: offers_pb2.OfferGroup,
    ) -> None:
        await self._offers.add(offer.SerializeToString(deterministic=True))
        await types.put_expires_at_if_less_than_current(
            self._redis,
            self._offers,
            offer.expires_at.ToDatetime(tzinfo=datetime.timezone.utc),
        )
