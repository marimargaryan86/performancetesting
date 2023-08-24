import enum

from pydantic.v1 import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.enums import PaymentStates
from snowfall.vendor.benerail.models.regex import UrlRegex


class PaymentMethod(enum.Enum):
    ac = "urn:itti:form_of_payment:AC"


class PaymentMethodProp(ConstrainedStr):
    regex = "^urn:[a-z]*:form_of_payment:[A-Z]*$"


class FormOfPaymentURN(BenerailBaseModel):
    __root__: PaymentMethodProp


class Price(BenerailBaseModel):
    amount: float = Field(
        ...,
        description="the number of decimals show the accuracy",
    )
    currency: str = Field(..., example="EUR")


class PaymentIdBody(BenerailBaseModel):
    payment_method: PaymentMethodProp
    amount: Price | None = None
    state: PaymentStates | None = None


class OrderIdPaymentsBody(BenerailBaseModel):
    payment_method: PaymentMethodProp
    amount: Price | None = None
    additional_info: dict[str, str] | None = None
    payment_webhook: UrlRegex | None = Field(
        None,
        example="https://www.benecustomer.com/payment-webhook/12345",
    )


class FormOfPayment(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:itti:form_of_payment:AC",
    )
    payment_value: PaymentMethodProp | None = Field(
        None,
        alias="value",
    )


class Payment(BenerailBaseModel):
    identifier: str = Field(..., alias="id")
    booking_id: str | None = None
    order_id: str | None = None
    payment_method: FormOfPayment | None = None
    payment_date: str | None = None
    payment_webhook: UrlRegex | None = None
    payment_amount: Price | None = None
    result_balance: float | None = None
    state: PaymentStates | None = None
