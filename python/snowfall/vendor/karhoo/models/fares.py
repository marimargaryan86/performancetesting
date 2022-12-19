import datetime
from typing import Literal

from snowfall.vendor.karhoo.models.base import KarhooBaseModel


class Base(KarhooBaseModel):
    tax_percentage: int | None
    commission_percentage: int | None
    tax_amount: int | None
    net_price: int | None


class Commission(KarhooBaseModel):
    tax_percentage: int | None
    tax_amount: int | None


class Extra(KarhooBaseModel):
    tax_percentage: int | None
    commission_percentage: int | None
    tax_amount: int | None
    net_price: int | None
    name: str | None


class Breakdown(KarhooBaseModel):
    base: Base | None
    commission: Commission | None
    extras: list[Extra] | None
    expenses: list[Extra] | None
    total: int | None
    currency: str | None


class FinalFare(KarhooBaseModel):
    state: Literal[
        "PENDING",
        "FINAL",
        "CANCELLED",
        "FAILED",
    ]
    expected_final_time: datetime.datetime | None
    expected_in: int | None
    breakdown: Breakdown | None
