from typing import Any

import pydantic

from snowfall.vendor.benerail.enums import PaymentStates
from snowfall.vendor.benerail.models.base import BenerailBaseModel


class Price(BenerailBaseModel):
    amount: float | None
    currency: str | None


class PaymentsIdBody(BenerailBaseModel):
    payment_method: str
    amount: Price | None


class OrderIdPaymentsBody(BenerailBaseModel):
    payment_method: str
    amount: Price | None
    additional_info: dict[Any, str] | None
    payment_webhook: str | None


class FormOfPayment(BenerailBaseModel):
    href: str | None
    form_of_payment_value: str | None = pydantic.Field(..., alias="value")


class Payment(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    booking_id: str | None
    order_id: str | None
    payment_method: FormOfPayment | None
    payment_date: str | None
    payment_webhook: str | None
    payment_amount: Price | None
    result_balance: int | None
    state: PaymentStates | None
