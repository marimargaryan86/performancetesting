"""Contains order request schemas."""
import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.util import passenger_enums


class Phone(BaseSchema):
    """Phone schema."""

    phone_type: passenger_enums.PhoneTypeEnum = pydantic.Field(..., alias="type")
    number: str = pydantic.Field(description="Phone number, including country code")


class Address(BaseSchema):
    """Address schema."""

    street1: str = pydantic.Field(description="Street 1")
    street2: str | None = pydantic.Field(description="Street 2")
    city: str = pydantic.Field(description="City name")
    zip_code: str = pydantic.Field(description="Zip code", alias="zip")
    country_code: str = pydantic.Field(description="Country code")


class Contact(BaseSchema):
    """Contact simple schema."""

    email: str = pydantic.Field(description="E-mail address")
    phone: Phone = pydantic.Field(description="Phone number")


class ContactDetailed(Contact):
    """Contact schema."""

    passenger_id: str = pydantic.Field(description="Passenger ID")
    address: Address = pydantic.Field(description="Address")
