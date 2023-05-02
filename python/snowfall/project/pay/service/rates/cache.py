import datetime

from snowfall.stdlib.persistence.redis import types as redis


class RateRepository(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: int = 5,
    ) -> None:
        self._redis = redis_client
        self._default_ttl = cache_ttl

    async def store(self, currency_pair: str, rate: float) -> None:
        await self._redis.put(currency_pair, str(rate))

        await self._redis.put_expires_at(
            currency_pair,
            datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(minutes=self._default_ttl),
        )

    async def get(self, currency_pair: str) -> float | None:
        rate = await self._redis.get(currency_pair)

        if rate:
            return round(float(rate), 2)

        return None
