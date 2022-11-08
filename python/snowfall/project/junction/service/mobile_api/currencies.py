import datetime
import time
from typing import Hashable

import asyncstdlib

from snowfall.project.junction.adapter import currencies


class CurrencyClient(object):
    def __init__(
        self,
        cache_ttl: datetime.timedelta,
        currencies_client: currencies.Client,
    ) -> None:
        self._cache_ttl = cache_ttl
        self._currencies_client = currencies_client

    def get_ttl_hash(self) -> int:
        return round(time.time() / self._cache_ttl.total_seconds())

    @asyncstdlib.lru_cache
    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        ttl_hash: Hashable = None,
    ) -> float:
        return await self._currencies_client.get_rate(
            from_currency,
            to_currency,
            1000,
        )
