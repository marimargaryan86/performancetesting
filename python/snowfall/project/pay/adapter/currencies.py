from __future__ import annotations

import abc
from collections.abc import Mapping

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib.money import Currency


class Client(abc.ABC):
    @abc.abstractmethod
    async def convert(
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
    ) -> models_pb2.Quote:
        """Convert amount from one currency to another."""


class DictClient(Client):
    def __init__(self, currencies: Mapping[tuple[str, str], float]):
        self._currencies = currencies

    async def convert(
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
    ) -> models_pb2.Quote:
        rate = self._currencies.get((from_currency.code, to_currency.code))
        if rate is None:
            raise errors.NotFoundError()

        return models_pb2.Quote(amount=int(amount * rate), rate=rate)


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
    ) -> models_pb2.Quote:
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
        return models_pb2.Quote(
            amount=response.amount,
            rate=float(
                "{0:.2f}".format(response.rate),
            ),
        )
