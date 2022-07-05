from __future__ import annotations

import abc
from typing import Mapping

import grpc

from snowfall.project.junction.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
)


class NotFoundError(Exception):
    """Raised when a currency is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def convert(
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
    ) -> int:
        """Convert amount from one currency to another."""


class DictClient(Client):
    def __init__(self, currencies: Mapping[tuple[str, str], float]):
        self._currencies = currencies

    async def convert(
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
    ) -> int:
        rate = self._currencies.get((from_currency, to_currency))
        if rate is None:
            raise NotFoundError()

        return int(amount * rate)


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
        from_currency: str,
        to_currency: str,
        amount: int,
    ) -> int:
        try:
            response = await self._currencies.Convert(
                currencies_pb2.ConvertRequest(
                    to_currency=to_currency,
                    from_currency=from_currency,
                    amount=amount,
                ),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Currency not found.",
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.amount
