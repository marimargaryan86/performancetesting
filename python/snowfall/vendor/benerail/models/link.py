from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel


class ResourceLink(BenerailBaseModel):
    href: str | None
    title: str | None


class LinkToRcode(BenerailBaseModel):
    href: str | None
    link_to_rcode_value: str | None = pydantic.Field(..., alias="value")


class RcodeLink(BenerailBaseModel):
    href: str | None
    rcode_link_value: str | None = pydantic.Field(..., alias="value")


class Link(BenerailBaseModel):
    href: str | None
    title: str | None
    rel: str | None
    link_type: Literal[
        "POST",
        "GET",
        "PUT",
        "DELETE",
    ] | None = pydantic.Field(..., alias="type")


class Supplier(BenerailBaseModel):
    href: str | None
    supplier_value: str | None = pydantic.Field(..., alias="value")


class LinkToBinary(BenerailBaseModel):
    href: str | None
    title: str | None
    link_format: Literal["application/pdf", "image/png"] | None = pydantic.Field(
        ...,
        alias="format",
    )
