from typing import Sequence

from snowfall.project.pay.service.rates.rates import BackUpRatesRepository
from snowfall.project.pay.service.rates.v1alpha import models_pb2
from snowfall.vendor.apilayer.client import APILayer


class UpdateBackUpRatesJob(object):
    def __init__(
        self,
        source_currencies: Sequence[str],
        backup_rates: BackUpRatesRepository,
        apilayer_client: APILayer,
    ):
        self._source_currencies = source_currencies
        self._backup_rates_repository = backup_rates
        self._apilayer_client = apilayer_client

    async def run(self) -> None:
        backup_rates = await self._get_backup_rates()
        await self._backup_rates_repository.delete_all()
        await self._backup_rates_repository.insert_many(backup_rates)

    async def _get_backup_rates(self) -> list[models_pb2.BackUpRate]:
        backup_rates: list[models_pb2.BackUpRate] = []

        for currency in self._source_currencies:
            rates = await self._apilayer_client.get_rates(currency, "")

            for rate in rates:
                backup_rates.append(
                    models_pb2.BackUpRate(
                        buy_currency=rate.buy_currency,
                        sell_currency=rate.sell_currency,
                        rate=rate.rate,
                    ),
                )

        return backup_rates
