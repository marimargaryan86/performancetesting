from pydantic import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.enums import Format, RequestType


class ResourceLink(BenerailBaseModel):
    href: AnyUrl
    title: str | None = Field(
        None,
        description="human-readable string representing the linked resource",
    )


class LinkToRcode(BenerailBaseModel):
    href: AnyUrl
    link_value: AnyUrl | None = Field(
        None,
        description="eg. urn:bnds:railteam_flexibility:MF",
        alias="value",
    )


class RcodeLink(BenerailBaseModel):
    href: AnyUrl
    link_value: ConstrainedStr | None = Field(
        None,
        description="eg. urn:bnds:railteam_flexibility:MF",
        alias="value",
        regex="^urn:[a-z]*:[a-z_]*:[A-Z_0-9]*$",
    )


class Link(BenerailBaseModel):
    href: AnyUrl
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
    href: AnyUrl
    title: str | None = Field(None, description="Info on referred value")
    link_format: Format | None = Field(None, alias="format")
