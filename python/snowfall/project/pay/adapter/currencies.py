from __future__ import annotations

import abc
from collections.abc import Mapping, Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.money import Currency

_DEFAULT_PAGE_SIZE = 20


class Client(abc.ABC):
    @abc.abstractmethod
    async def convert(
        self,
        from_currency: Currency,
        to_currency: Currency,
        amount: int,
    ) -> models_pb2.Quote:
        """Convert amount from one currency to another."""

    @abc.abstractmethod
    async def get(
        self,
        currency: str,
        *,
        no_exist_ok: bool = False,
    ) -> models_pb2.Currency | None:
        """Check is currency in supported list."""

    @abc.abstractmethod
    async def find(
        self,
        cursor: str | None,
        limit: int | None,
    ) -> currencies_pb2.FindResponse:
        """Get currencies list."""


class DictClient(Client):
    def __init__(
        self,
        currencies: Mapping[tuple[str, str], float],
        supported_currencies: Sequence[Currency],
    ):
        self._currencies = currencies
        sorted_currencies = sorted(
            supported_currencies,
            key=lambda curr: curr.code,
        )
        self._supported_currencies = {curr.code: curr for curr in sorted_currencies}

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

    async def get(
        self,
        currency: str,
        *,
        no_exist_ok: bool = False,
    ) -> models_pb2.Currency | None:
        iso_currency = self._supported_currencies.get(currency)
        if iso_currency is None:
            if no_exist_ok:
                return None
            raise errors.NotFoundError()

        return models_pb2.Currency(
            code=iso_currency.code,
            name=iso_currency.currency_name,
            exponent=iso_currency.exponent or 0,
        )

    async def find(
        self,
        cursor: str | None,
        limit: int | None,
    ) -> currencies_pb2.FindResponse:
        page = sequence.paginate(
            sequence=tuple(self._supported_currencies.values()),
            cursor=cursor,
            limit=limit or _DEFAULT_PAGE_SIZE,
        )
        return currencies_pb2.FindResponse(
            currencies=[
                models_pb2.Currency(
                    code=currency.code,
                    name=currency.currency_name,
                    exponent=currency.exponent or 0,
                )
                for currency in page.sequence
            ],
            next_page_token=page.cursor,
        )


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

    async def get(
        self,
        currency: str,
        *,
        no_exist_ok: bool = False,
    ) -> models_pb2.Currency | None:
        get_coroutine = errors.handle_grpc_errors(
            self._currencies.Get(
                currencies_pb2.GetRequest(
                    currency=currency,
                ),
            ),
        )
        if no_exist_ok:
            try:
                return (await get_coroutine).currency
            except errors.NotFoundError:
                return None
        return (await get_coroutine).currency

    async def find(
        self,
        cursor: str | None,
        limit: int | None,
    ) -> currencies_pb2.FindResponse:
        return await self._currencies.Find(
            currencies_pb2.FindRequest(
                page_size=limit or _DEFAULT_PAGE_SIZE,
                page_token=cursor or "",
            ),
        )
