from snowfall.project.pay.service.rates.rates import (
    MonitoredRatesRepository,
    RatesRepository,
)
from snowfall.project.pay.service.rates.v1alpha import models_pb2
from snowfall.vendor.bound.client import Bound


class FetchRateJob(object):
    def __init__(
        self,
        rates: RatesRepository,
        monitored_rates: MonitoredRatesRepository,
        bound_client: Bound,
    ):
        self._rates = rates
        self._monitored_rates = monitored_rates
        self._bound_client = bound_client

    async def run(self) -> None:
        currency_pairs = await self._generate_currency_pairs()
        rates = await self._bound_client.get_rates(currency_pairs)

        await self._rates.insert_many(
            [
                models_pb2.Rate(
                    buy_currency=rate.buy_currency,
                    sell_currency=rate.sell_currency,
                    rate=rate.rate,
                )
                for rate in rates
            ],
        )

    async def _generate_currency_pairs(self) -> str:
        monitored_currencies = await self._monitored_rates.find_enabled_rates()
        pairs = set()
        async for currency in monitored_currencies:
            pairs.add(
                "{0}{1},{1}{0}".format(currency.buy_currency, currency.sell_currency),
            )

        return ",".join(pairs)
