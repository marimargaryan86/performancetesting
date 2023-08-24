"""Contains common response schemas."""

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.util import passenger_enums


class Phone(BaseSchema):
    """Phone schema."""

    phone_type: passenger_enums.PhoneTypeEnum = pydantic.Field(
        description="Phone type",
        alias="type",
    )
    number: str = pydantic.Field(description="Phone number, including country code")


class Contact(BaseSchema):
    """Contact schema."""

    email: str = pydantic.Field(description="Contact E-mail address")
    phone: Phone = pydantic.Field(description="Contact phone number")


class PassengerSimple(BaseSchema):
    """Passenger simple schema."""

    identifier: str = pydantic.Field(..., alias="id")
    passenger_type: passenger_enums.PassengerTypeEnum = pydantic.Field(
        description="Passenger type",
        alias="type",
    )


class PaymentCard(BaseSchema):
    """Payment card schema."""

    code: str = pydantic.Field(description="Code")
    name: str = pydantic.Field(description="Name")
    payment_type: passenger_enums.PaymentCardTypeEnum = pydantic.Field(
        description="Type",
        alias="type",
    )
