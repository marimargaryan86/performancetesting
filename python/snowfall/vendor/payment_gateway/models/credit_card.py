from pydantic import Field

from snowfall.vendor.payment_gateway.models.base import BaseModel


class BillingAddress(BaseModel):
    country: str | None = None
    country_code: str
    state: str | None = None
    state_code: str
    city: str
    address1: str
    address2: str | None = None
    zip_code: str
    street_number: str | None = None


class CreditCardAttributes(BaseModel):
    number: str = Field(
        pattern=r"^\d{16}$",
        examples=["4242424242424242"],
        description="The credit card number must be exactly 16 digits long.",
    )
    cvc: str = Field(
        pattern=r"^\d{3}$",
        examples=["345"],
        description="The card verification code, which must be 3 digits long.",
    )
    expiration: str = Field(
        examples=["03/2026"],
        pattern=r"^(0[1-9]|1[0-2])\/([0-9]{4})$",
        description="Expiration date in the format MM/YYYY",
    )
    holder_name: str
    billing_address: BillingAddress
    is_default: bool | None = None
    reservation_types: int | None = None


class CreditCardDataRequest(BaseModel):
    attributes: CreditCardAttributes
    type: str = "credit-cards"


class CreditCardRequest(BaseModel):
    data: CreditCardDataRequest


class CreditCardResponseAttributes(BaseModel):
    name: str | None = None
    address: BillingAddress | None
    is_default: bool | None
    brand: str | None = None
    exp_date: str | None
    last_digits: str | None
    type: str | None = None
    holder_name: str | None
    reservation_types: int | None


class CreditCardDataResponse(BaseModel):
    id: int
    attributes: CreditCardResponseAttributes
    type: str = "credit-cards"


class CreditCardResponse(BaseModel):
    data: CreditCardDataResponse
