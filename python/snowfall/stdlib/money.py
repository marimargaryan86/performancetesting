from __future__ import annotations

import contextlib
import dataclasses
import functools

import iso4217

from snowfall.stdlib.v1alpha import money_pb2

Currency = iso4217.Currency


@functools.cache
def _exponent(currency: Currency) -> int:
    return 10**currency.exponent


@functools.cache
def _nano_exponent(currency: Currency) -> int:
    return 10 ** (9 - currency.exponent)


@dataclasses.dataclass(frozen=True)
class Money(object):
    amount: int
    currency: Currency

    def __str__(self) -> str:
        if self.currency.exponent == 0:
            return "{symbol}{unit}".format(
                symbol="-" if self.amount < 0 else "",
                unit=abs(self.amount) // _exponent(self.currency),
            )

        return "{symbol}{unit}.{subunit:0{width}d}".format(
            symbol="-" if self.amount < 0 else "",
            unit=abs(self.amount) // _exponent(self.currency),
            subunit=abs(self.amount) % _exponent(self.currency),
            width=self.currency.exponent,
        )

    def add(self, money: Money) -> Money:
        if self.currency != money.currency:
            raise RuntimeError("Can't add money in two different currencies.")

        return Money(self.amount + money.amount, self.currency)

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
    parts = string_amount.split(separator, 1)
    units = int(parts[0])
    amount = abs(units) * _exponent(currency)

    with contextlib.suppress(IndexError):
        amount += int(parts[1])

    return Money(
        amount=-amount if units < 0 else amount,
        currency=currency,
    )
