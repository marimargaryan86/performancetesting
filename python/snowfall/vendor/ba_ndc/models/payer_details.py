from typing import Literal

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

    address: Address = pydantic.Field(description="Address")


class PayerDetails(BaseSchema):
    """Payer details schema."""

    payer_details_type: Literal["passenger", "third_party"] = pydantic.Field(
        ...,
        alias="type",
    )
    contact: ContactDetailed = pydantic.Field(description="Contact information")


class PayerDetailsPassenger(PayerDetails):
    """Payer details passenger schema."""

    payer_details_type: Literal["passenger"] = pydantic.Field(
        ...,
        alias="type",
    )
    passenger_id: str = pydantic.Field(description="Passenger identifier")


class PayerDetailsThirdParty(PayerDetails):
    """Payer details third party schema."""

    payer_details_type: Literal["third_party"] = pydantic.Field(
        ...,
        alias="type",
    )
    first_name: str = pydantic.Field(description="Payer first name")
    last_name: str = pydantic.Field(description="Payer last name")
    name_title: str = pydantic.Field(description="Payer name title")
