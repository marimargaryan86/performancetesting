"""Contains order request schemas."""

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.response_common_passenger_schemas import Contact


class Address(BaseSchema):
    """Address schema."""

    street1: str = pydantic.Field(description="Street 1")
    street2: str | None = pydantic.Field(description="Street 2")
    city: str = pydantic.Field(description="City name")
    zip_code: str = pydantic.Field(description="Zip code", alias="zip")
    country_code: str = pydantic.Field(description="Country code")


class ContactDetailed(Contact):
    """Contact schema."""

    passenger_id: str = pydantic.Field(description="Passenger ID")
    address: Address = pydantic.Field(description="Address")
