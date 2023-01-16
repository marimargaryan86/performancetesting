from __future__ import annotations

import abc
from typing import Mapping

from snowfall.project.junction.adapter import errors
from snowfall.project.junction.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
)
from snowfall.stdlib.money import Currency


class Client(abc.ABC):
    @abc.abstractmethod
    async def convert(
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
    ) -> int:
        """Convert amount from one currency to another."""

    @abc.abstractmethod
    async def get_rate(
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
    ) -> float:
        """Get rate for conversion."""


class DictClient(Client):
    def __init__(self, currencies: Mapping[tuple[str, str], float]):
        self._currencies = currencies

    async def convert(
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
    ) -> int:
        rate = self._currencies.get((from_currency.code, to_currency.code))
        if rate is None:
            raise errors.NotFoundError()

        return int(amount * rate)

    async def get_rate(
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
    ) -> float:
        rate = self._currencies.get((from_currency.code, to_currency.code))
        if rate is None:
            raise errors.NotFoundError()

        return rate


class GrpcClient(Client):
    def __init__(
        self,
        currencies: currencies_pb2_grpc.CurrencyServiceStub,
        timeout: int = 10,
    ):
        self._currencies = currencies
        self._timeout = timeout

    async def convert(
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
    ) -> int:
        response = await errors.handle_grpc_errors(
            self._currencies.Convert(
                currencies_pb2.ConvertRequest(
                    to_currency=to_currency.code,
                    from_currency=from_currency.code,
                    amount=amount,
                ),
                timeout=self._timeout,
            ),
        )

        return response.amount

    async def get_rate(
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
    ) -> float:
        response = await errors.handle_grpc_errors(
            self._currencies.Convert(
                currencies_pb2.ConvertRequest(
                    to_currency=to_currency.code,
                    from_currency=from_currency.code,
                    amount=amount,
                ),
                timeout=self._timeout,
            ),
        )

        return float("{0:.2f}".format(response.rate))
