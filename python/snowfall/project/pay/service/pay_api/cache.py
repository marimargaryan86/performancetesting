import datetime

from redis.asyncio import lock

from snowfall.stdlib.persistence.redis import types as redis


class UserSessionRepository(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
    ) -> None:
        self._redis = redis_client
        self._default_ttl = cache_ttl

    async def store(self, identifier: str, currency_pair: str, rate: float) -> None:
        session = self._redis.hash_(identifier)
        cache_key = "{0}:{1}".format(identifier, currency_pair)

        async with self._redis.lock(cache_key):
            await session.put(currency_pair, str(rate))

            ttl = await self._redis.get_expires_at(identifier)

            if not ttl:
                ttl = datetime.datetime.now(tz=datetime.UTC) + self._default_ttl

            await session.put(currency_pair, str(rate))

            await self._redis.put_expires_at(session, ttl)

    async def get_rate(self, identifier: str, currency_pair: str) -> float | None:
        session = self._redis.hash_(identifier)
        rate = await session.get(currency_pair)

        if rate:
            return float(rate)

        cache_key = "{0}:{1}".format(identifier, currency_pair)
        async with self._redis.lock(cache_key):
            rate = await session.get(currency_pair)
            if rate:
                return float(rate)

        return None

    async def lock(self, cache_key: str) -> lock.Lock:
        return self._redis.lock(cache_key)
