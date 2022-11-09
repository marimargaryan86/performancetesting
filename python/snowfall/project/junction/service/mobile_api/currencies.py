import datetime
import time
from typing import Hashable, Mapping

import asyncstdlib

from snowfall.project.junction.adapter import currencies, errors


class CurrencyClient(object):
    def __init__(
        self,
        cache_ttl: datetime.timedelta,
        currencies_client: currencies.Client,
        fallback_rates: Mapping[str, float],
    ) -> None:
        self._cache_ttl = cache_ttl
        self._currencies_client = currencies_client
        self._fallback_rates = fallback_rates

    def get_ttl_hash(self) -> int:
        return round(time.time() / self._cache_ttl.total_seconds())

    @asyncstdlib.lru_cache
    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        ttl_hash: Hashable = None,
    ) -> float:
        try:
            return await self._currencies_client.get_rate(
                from_currency,
                to_currency,
                1000,
            )
        except errors.UnhandledError as err:
            rate = self._fallback_rates.get(to_currency)
            if not rate:
                raise err
            return rate
