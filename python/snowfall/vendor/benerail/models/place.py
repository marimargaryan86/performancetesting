from pydantic.v1 import AnyUrl, Field

from snowfall.vendor.benerail.models import types
from snowfall.vendor.benerail.models.base import BenerailBaseModel


class AddressDetail(BenerailBaseModel):
    country_name: str | None = Field(
        None,
        description="Country of the address.",
        example="The Netherlands",
    )
    post_code: str | None = Field(
        None,
        description="Postal code of the address.",
        example="2265CA",
    )
    street: str | None = Field(
        None,
        description="Street name of the address.",
        example="Oude Trambaan",
    )
    house_number: str | None = Field(
        None,
        example="7",
    )


class Address(AddressDetail):
    address_name: str = Field(
        ...,
        description="Name or description of address for use in passenger information.",
        example="Oude Trambaan 7, 2265CA Leidschendam, Nederland",
    )


class Place(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:bnds:tstatn_id:NLASC",
    )
    place_value: types.PlaceUrnStr = Field(..., alias="value")
