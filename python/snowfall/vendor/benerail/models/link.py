from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel


class ResourceLink(BenerailBaseModel):
    href: str | None
    title: str | None


class LinkToRcode(BenerailBaseModel):
    href: str | None
    link_to_rcode_value: str | None = pydantic.Field(..., alias="value")


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


class TrainType1(BenerailBaseModel):
    href: str | None
    train_type_value: str | None = pydantic.Field(..., alias="value")


class TrainType(BenerailBaseModel):
    train_type: str | None
    preference_type: Literal["REQUIRED", "UNACCEPTABLE"] | None


class Supplier(BenerailBaseModel):
    href: str | None
    supplier_value: str | None = pydantic.Field(..., alias="value")
