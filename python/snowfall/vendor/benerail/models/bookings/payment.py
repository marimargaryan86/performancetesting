from pydantic import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.enums import PaymentStates
from snowfall.vendor.benerail.models.regex import UrlRegex


class FormOfPaymentURN(BenerailBaseModel):
    __root__: ConstrainedStr = Field(
        ...,
        example="urn:itti:form_of_payment:AC",
        regex="^urn:[a-z]*:form_of_payment:[A-Z]*$",
    )


class Price(BenerailBaseModel):
    amount: float | None = Field(
        None,
        description="the number of decimals show the accuracy",
    )
    currency: str | None = Field(None, example="EUR")


class PaymentIdBody(BenerailBaseModel):
    payment_method: FormOfPaymentURN
    amount: Price | None = None


class OrderIdPaymentsBody(BenerailBaseModel):
    payment_method: FormOfPaymentURN
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
    payment_value: ConstrainedStr | None = Field(
        None,
        example="urn:itti:form_of_payment:AC",
        alias="value",
        regex="^urn:[a-z]*:form_of_payment:[A-Z]*$",
    )


class Payment(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    booking_id: str | None = None
    order_id: str | None = None
    payment_method: FormOfPayment | None = None
    payment_date: str | None = None
    payment_webhook: UrlRegex | None = None
    payment_amount: Price | None = None
    result_balance: float | None = None
    state: PaymentStates | None = None
