import asyncio
from collections.abc import Sequence

from httpx import HTTPStatusError

from snowfall.project.pay.service.rates.cache import RateRepository
from snowfall.project.pay.service.rates.rates import BackUpRatesRepository
from snowfall.project.pay.service.rates.v1alpha import models_pb2
from snowfall.stdlib.logging import stdout
from snowfall.vendor.xe.client import XEClient

_logger = stdout.get_logger()


class UpdateBackUpRatesJob:
    def __init__(
        self,
        backup_rates: BackUpRatesRepository,
        xe_client: XEClient,
        available_currencies: list[str],  # noqa: SF20
        redis_client: RateRepository,
    ):
        self._backup_rates_repository = backup_rates
        self._available_currencies = available_currencies
        self._xe_client = xe_client
        self._redis_client = redis_client

    async def run(self) -> None:
        backup_rates = await self._get_rates()
        if backup_rates:
            await self._backup_rates_repository.delete_all()
            await self._backup_rates_repository.insert_many(backup_rates)
            await self._cache_rates(backup_rates)

    async def _get_rates(self) -> list[models_pb2.BackUpRate]:
        rates = [
            self._xe_client.convert(
                self._available_currencies[index],
                self._available_currencies[:index]
                + self._available_currencies[index + 1 :],
            )
            for index in range(len(self._available_currencies))
        ]

        rates_gather = await asyncio.gather(*rates, return_exceptions=True)

        rate_results: list[models_pb2.BackUpRate] = []
        for rate_result in rates_gather:
            if isinstance(rate_result, HTTPStatusError):
                response = rate_result.response.json()
                _logger.error(
                    response["message"],
                    status_code=rate_result.response.status_code,
                )
                continue
            if isinstance(rate_result, BaseException):
                raise rate_result
            rate_results.extend(
                models_pb2.BackUpRate(
                    buy_currency=rate.to_currency,
                    sell_currency=rate.from_currency,
                    rate=rate.rate,
                )
                for rate in rate_result
            )
        return rate_results

    async def _cache_rates(self, rates: Sequence[models_pb2.BackUpRate]) -> None:
        for rate in rates:
            await self._redis_client.store(
                "{0}{1}".format(rate.sell_currency, rate.buy_currency),
                rate.rate,
            )
