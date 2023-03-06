import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel


class AddressDetail(BenerailBaseModel):
    country_name: str | None
    post_code: str | None
    street: str | None
    house_number: str | None


class Address(BenerailBaseModel):
    address_name: str
    country_name: str | None
    post_code: str | None
    street: str | None
    house_number: str | None


class Place(BenerailBaseModel):
    href: str | None
    place_value: str | None = pydantic.Field(..., alias="value")
