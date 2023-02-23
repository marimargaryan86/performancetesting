from typing import Literal

import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.response_common_passenger_schemas import Contact


class Address(BaseSchema):
    """Address schema."""

    address_lines: list[str] = pydantic.Field(description="Address lines")
    city: str = pydantic.Field(description="City name")
    zip_code: str = pydantic.Field(description="Zip code", alias="zip")
    country_code: str = pydantic.Field(description="Country code")


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
