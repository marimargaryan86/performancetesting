from abc import ABC
from decimal import Decimal
from typing import Literal

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.payer_details import (
    PayerDetailsPassenger,
    PayerDetailsThirdParty,
)


class ExpiryDate(BaseSchema):
    """Expiry date schema."""

    month: int = pydantic.Field(description="Expiry month")
    year: int = pydantic.Field(description="Expiry year")


class Payment(BaseSchema, ABC):
    """Payment schema."""

    payment_type: Literal["cash", "card", "voucher"] = pydantic.Field(alias="type")
    payer_details: PayerDetailsPassenger | PayerDetailsThirdParty = pydantic.Field(
        description="Payer details",
        discriminator="payer_details_type",
    )


class CreditCardPayment(Payment):
    """Credit card payment schema."""

    payment_type: Literal["card"] = pydantic.Field(..., alias="type")
    code: str = pydantic.Field(description="Card code")
    number: str = pydantic.Field(description="Card number")
    cvc: str = pydantic.Field(description="Card CVC")
    holder_name: str = pydantic.Field(description="Card holder name")
    expiry_date: ExpiryDate = pydantic.Field(description="Card expiry date")


class CashPayment(Payment):
    """Cash payment schema."""

    payment_type: Literal["cash"] = pydantic.Field(
        description="Cash payment type",
        alias="type",
    )
    currency_code: str = pydantic.Field(description="Currency code")
    amount: Decimal = pydantic.Field(description="Amount")


class VoucherPayment(Payment):
    """Voucher payment schema."""

    payment_type: Literal["voucher"] = pydantic.Field(..., alias="type")
    # TODO(alvaro.g): Impl.
