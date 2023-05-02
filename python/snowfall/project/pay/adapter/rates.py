from __future__ import annotations

import abc
from typing import Mapping

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.rates.v1alpha import (
    models_pb2,
    rates_pb2,
    rates_pb2_grpc,
)
from snowfall.stdlib.money import Currency


class Client(abc.ABC):
    @abc.abstractmethod
    async def get_rate(
        self,
        sell_currency: Currency,
        buy_currency: Currency,
    ) -> models_pb2.Rate:
        """Convert amount from one currency to another."""


class DictClient(Client):
    def __init__(self, rates: Mapping[tuple[str, str], float]):
        self._rates = rates

    async def get_rate(
        self,
        sell_currency: Currency,
        buy_currency: Currency,
    ) -> models_pb2.Rate:
        rate = self._rates.get((sell_currency.code, buy_currency.code))
        if rate is None:
            raise errors.NotFoundError()

        return models_pb2.Rate(
            sell_currency=sell_currency.code,
            buy_currency=buy_currency.code,
            rate=rate,
        )


class GrpcClient(Client):
    def __init__(
        self,
        rates: rates_pb2_grpc.RatesServiceStub,
        timeout: int = 10,
    ):
        self._rates = rates
        self._timeout = timeout

    async def get_rate(
        self,
        sell_currency: Currency,
        buy_currency: Currency,
    ) -> models_pb2.Rate:
        response = await errors.handle_grpc_errors(
            self._rates.Get(
                rates_pb2.GetRequest(
                    sell_currency=sell_currency.code,
                    buy_currency=buy_currency.code,
                ),
                timeout=self._timeout,
            ),
        )
        return models_pb2.Rate(
            sell_currency=sell_currency.code,
            buy_currency=buy_currency.code,
            rate=response.rate.rate,
        )
