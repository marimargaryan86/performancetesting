from __future__ import annotations

import contextlib
import dataclasses
import decimal
import functools
from collections.abc import Iterable

import iso4217

from snowfall.stdlib.v1 import money_pb2

Currency = iso4217.Currency


@functools.cache
def _int_exponent(currency: Currency) -> int:
    return currency.exponent or 0


@functools.cache
def _exponent(currency: Currency) -> int:
    return 10 ** _int_exponent(currency)


@functools.cache
def _nano_exponent(currency: Currency) -> int:
    return 10 ** (9 - _int_exponent(currency))


@dataclasses.dataclass(frozen=True)
class Money(object):
    amount: int
    currency: Currency

    def __str__(self) -> str:
        if _int_exponent(self.currency) == 0:
            return "{symbol}{unit}".format(
                symbol="-" if self.amount < 0 else "",
                unit=abs(self.amount) // _exponent(self.currency),
            )

        return "{symbol}{unit}.{subunit:0{width}d}".format(  # noqa: PLE1300
            symbol="-" if self.amount < 0 else "",
            unit=abs(self.amount) // _exponent(self.currency),
            subunit=abs(self.amount) % _exponent(self.currency),
            width=_int_exponent(self.currency),
        )

    def add(self, money: Money) -> Money:
        if self.currency != money.currency:
            raise RuntimeError("Can't add money in two different currencies.")

        return Money(self.amount + money.amount, self.currency)

    def convert(self, currency: Currency, rate: decimal.Decimal) -> Money:
        diff = decimal.Decimal(
            str(10 ** (_int_exponent(self.currency) - _int_exponent(currency))),
        )

        return Money(int(round(self.amount * rate / diff)), currency)

    def protobuf(self) -> money_pb2.Money:
        units = abs(self.amount) // _exponent(self.currency)
        remainder = abs(self.amount) % _exponent(self.currency)
        nanos = remainder * _nano_exponent(self.currency)

        return money_pb2.Money(
            currency_code=self.currency.code,
            units=-units if self.amount < 0 else units,
            nanos=-nanos if self.amount < 0 else nanos,
        )


def from_protobuf(proto: money_pb2.Money) -> Money:
    currency = Currency(proto.currency_code)
    units = abs(proto.units) * _exponent(currency)
    nanos = abs(proto.nanos) // _nano_exponent(currency)
    amount = units + nanos

    return Money(
        amount=-amount if proto.units < 0 else amount,
        currency=currency,
    )


def from_string(
    string_amount: str,
    currency: Currency,
    separator: str = ".",
) -> Money:
    string_amount = string_amount.replace(separator, ".")
    rounded_amount = str(round(float(string_amount), _int_exponent(currency)))
    parts = rounded_amount.split(".", 1)
    units = int(parts[0])
    amount = abs(units) * _exponent(currency)

    with contextlib.suppress(IndexError):
        amount += int(parts[1].ljust(_int_exponent(currency), "0"))

    return Money(
        amount=-amount if units < 0 else amount,
        currency=currency,
    )


def total(moneys: Iterable[Money]) -> Money:
    return functools.reduce(lambda carry, money: carry.add(money), moneys)
