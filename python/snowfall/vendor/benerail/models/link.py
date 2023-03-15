from pydantic import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.enums import Format, RequestType


class ResourceLink(BenerailBaseModel):
    href: AnyUrl | None = Field(None, description="callable url")
    title: str | None = Field(
        None,
        description="human-readable string representing the linked resource",
    )


class LinkToRcode(BenerailBaseModel):
    href: AnyUrl | None = Field(None, description="callable url")
    link_value: AnyUrl | None = Field(
        None,
        description="eg. urn:bnds:railteam_flexibility:MF",
        alias="value",
    )


class RcodeLink(BenerailBaseModel):
    href: AnyUrl | None = Field(None, description="callable url")
    link_value: ConstrainedStr | None = Field(
        None,
        description="eg. urn:bnds:railteam_flexibility:MF",
        alias="value",
        regex="^urn:[a-z]*:[a-z_]*:[A-Z_0-9]*$",
    )


class Link(BenerailBaseModel):
    href: AnyUrl | None = None
    title: str | None = None
    rel: str | None = None
    link_type: RequestType | None = Field(
        None,
        description="GET is the default.",
        alias="type",
    )


class Supplier(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:itti:supplier:THA",
    )
    supplier_value: ConstrainedStr | None = Field(
        None,
        example="urn:itti:supplier:THA",
        alias="value",
        regex="^urn:itti:supplier:[A-Z_0-9]*$",
    )


class LinkToBinary(BenerailBaseModel):
    href: AnyUrl | None = Field(None, description="callable url")
    title: str | None = Field(None, description="Info on referred value")
    link_format: Format | None = Field(None, alias="format")


class ZonedDateTime(BenerailBaseModel):
    __root__: ConstrainedStr = Field(
        ...,
        example="2022-11-16T11:38+01:00",
        regex="^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12]["
        + "0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):?([0-5][0-9])?([+-](?:2[0-3]|["
        + "01][0-9]):[0-5][0-9])$",
    )
