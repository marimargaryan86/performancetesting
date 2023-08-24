from datetime import date

from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.enumeration.enums import ContentType


class RcodeAttributeType(BenerailBaseModel):
    last_update_at: date | None = Field(None, example="2020-10-25")
    attribute_type: str | None = Field(None, example="INCLUDES_TRAVELZONE")
    content_type: ContentType | None = None
    language_dependent: bool | None = None
    needs_value: bool | None = None
    description: str | None = None


class LinksUnderscoreType(BenerailBaseModel):
    self_page: str | None = Field(
        None,
        example="https://api.example.com/type?page=3",
        alias="self",
    )
    previous: str | None = Field(
        None,
        example="https://api.example.com/type?page=2",
    )
    next_page: str | None = Field(
        None,
        example="https://api.example.com/type?page=4",
        alias="next",
    )
    first: str | None = Field(None, example="https://api.example.com/type?page=0")
    last: str | None = Field(None, example="https://api.example.com/type?page=8")
    parent: str | None = Field(None, example="https://api.example.com/othertype")


class RcodeAttributeAttributeType(BenerailBaseModel):
    type_name: str | None = None
    href: str | None = None


class RcodeType(BenerailBaseModel):
    identifier: str | None = Field(None, example="TSTATN_ID", alias="id")
    description: str | None = Field(None, example="Description of the enumeration type")
    last_update_at: str | None = Field(
        None,
        example="2021-09-29T13:20:34.143+02:00",
    )
    attribute_types: str | None = Field(
        None,
        alias="attribute-types",
        example="http://www.example.org/rcode/rcode-type/TSTATN_ID/attribute-types",
    )
    authorizations: str | None = Field(
        None,
        example="http://www.example.org/rcode/rcode-type/TSTATN_ID/authorizations",
    )
    field_links: LinksUnderscoreType | None = Field(None, alias="_links")
