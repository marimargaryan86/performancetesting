import itertools
from typing import Sequence

from snowfall.project.pay.service.rates.cache import RateRepository
from snowfall.project.pay.service.rates.rates import BackUpRatesRepository
from snowfall.project.pay.service.rates.v1alpha import models_pb2
from snowfall.vendor.currency_cloud.client import PaymentClient

_CC_MAX_PAIR_SIZE = 2450


class UpdateBackUpRatesJob(object):
    def __init__(
        self,
        backup_rates: BackUpRatesRepository,
        cc_client: PaymentClient,
        available_currencies: Sequence[str],
        redis_client: RateRepository,
    ):
        self._backup_rates_repository = backup_rates
        self._available_currencies = available_currencies
        self._cc_client = cc_client
        self._redis_client = redis_client

    async def run(self) -> None:
        backup_rates = await self._get_rates()
        if backup_rates:
            await self._backup_rates_repository.delete_all()
            await self._backup_rates_repository.insert_many(backup_rates)
            await self._cache_rates(backup_rates)

    def _generate_pairs(self) -> list[str]:
        possible_currency_pairs = itertools.permutations(self._available_currencies, 2)

        currency_pairs = ",".join(
            ("{0}{1}".format(pair[0], pair[1]) for pair in possible_currency_pairs),
        )

        return self._split_pairs_to_chunks(currency_pairs, _CC_MAX_PAIR_SIZE)

    def _split_pairs_to_chunks(self, pairs: str, max_len: int) -> list[str]:
        chunks = []
        current_chunk = ""
        for pair in pairs:
            if len(current_chunk) + len(pair) > max_len:
                chunks.append(current_chunk)
                current_chunk = pair
            else:
                current_chunk += pair
        chunks.append(current_chunk)
        return chunks

    async def _get_rates(self) -> list[models_pb2.BackUpRate]:
        pair_chunks = self._generate_pairs()
        rates: list[models_pb2.BackUpRate] = []
        for chunk in pair_chunks:
            rates.extend(
                (
                    models_pb2.BackUpRate(
                        buy_currency=rate.buy_currency,
                        sell_currency=rate.sell_currency,
                        rate=rate.rate,
                    )
                    for rate in await self._cc_client.get_basic_rates(chunk)
                ),
            )
        return rates

    async def _cache_rates(self, rates: Sequence[models_pb2.BackUpRate]) -> None:
        for rate in rates:
            await self._redis_client.store(
                "{0}{1}".format(rate.sell_currency, rate.buy_currency),
                rate.rate,
            )
