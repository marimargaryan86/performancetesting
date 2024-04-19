import datetime

from redis.asyncio import lock

from snowfall.stdlib.persistence.redis import types as redis


class UserSessionRepository:
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
    ) -> None:
        self._redis = redis_client
        self._default_ttl = cache_ttl

    async def store(self, identifier: str, currency_pair: str, rate: float) -> None:
        session = self._redis.hash_(identifier)
        ttl = datetime.datetime.now(tz=datetime.UTC) + self._default_ttl

        await session.put(currency_pair, str(rate))

        await self._redis.put_expires_at(session, ttl)

    async def get_rate(self, identifier: str, currency_pair: str) -> float | None:
        session = self._redis.hash_(identifier)
        rate = await session.get(currency_pair)

        return float(rate) if rate else None

    def lock(self, cache_key: str) -> lock.Lock:
        return self._redis.lock(cache_key)
