from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.enumeration.authorization import (
    RcodeAuthorization,
    RcodeAuthorizationGroup,
)
from snowfall.vendor.benerail.models.enumeration.position import (
    Address,
    GeoPosition,
    PointOfInterest,
    Station,
)
from snowfall.vendor.benerail.models.enumeration.rcode import (
    RcodeAttribute,
    RcodeMetaData,
    RcoderesultLabels,
)
from snowfall.vendor.benerail.models.enumeration.rcode_types import (
    LinksUnderscoreType,
    RcodeAttributeType,
    RcodeType,
)


class AttributeTypesResult(BenerailBaseModel):
    attribute_types: list[RcodeAttributeType] | None = Field(
        None,
        alias="attribute-types",
    )
    field_links: LinksUnderscoreType | None = Field(None, alias="_links")


class TypesResult(BenerailBaseModel):
    types: list[RcodeType] | None = None


class AuthorizationGroupsResult(BenerailBaseModel):
    authorization_groups: list[RcodeAuthorizationGroup] | None = None
    field_links: LinksUnderscoreType | None = Field(None, alias="_links")


class RcodeResult(BenerailBaseModel):
    identifier: str | None = Field(
        None,
        description="The id is the UrlToken parameter",
        example="urn:bnds:tstatn_id:NLASC",
        alias="id",
    )
    code_id: int | None = None
    type_id: str | None = Field(None, example="TSTATN_ID")
    sorting_tag: int | None = None
    metadata: RcodeMetaData | None = None
    labels: dict[str, RcoderesultLabels] = Field(
        ...,
        example={
            "nl/nl": {
                "codeShort": "NLASC",
                "codeLong": "NLASC",
                "text": "Amsterdam Centraal Station",
            },
            "en": {
                "codeShort": "NLASC",
                "codeLong": "NLASC",
                "text": "Amsterdam Centraal Station",
            },
            "*": {
                "codeShort": "NLASC",
                "codeLong": "NLASC",
                "text": "Amsterdam Centraal Station",
            },
        },
    )
    codes: dict[str, str] | None = Field(
        None,
        example={
            "bnds": "urn:bnds:tstatn_id:NLASC",
            "uic": "urn:uic:tstatn_id:118400058",
            "pao": "urn:pao:tstatn_id:NLAMA",
        },
    )
    attributes: str | None = Field(
        None,
        description="URL where extra attributes for this code can be found",
        example="http://www.example.org/rcode/rcode/id/10/123456/attributes",
    )
    field_links: LinksUnderscoreType | None = Field(None, alias="_links")


class RcodesResult(BenerailBaseModel):
    rcodes: list[RcodeResult]
    field_links: LinksUnderscoreType | None = Field(None, alias="_links")


class PlaceResult(BenerailBaseModel):
    identifier: str | None = Field(
        None,
        description="The id is the URI of the place",
        example="urn:bnds:tstatn_id:NLASC",
        alias="id",
    )
    metadata: RcodeMetaData | None = None
    name: str | None = Field(
        None,
        example="Amsterdam Centraal",
    )
    geo_coordinate: GeoPosition | None = None
    address: Address | None = None
    place: Station | PointOfInterest | None = Field(None, discriminator="place_type")
    field_links: LinksUnderscoreType | None = Field(None, alias="_links")


class AttributesResult(BenerailBaseModel):
    attributes: list[RcodeAttribute] | None = None
    field_links: LinksUnderscoreType | None = Field(None, alias="_links")


class AuthorizationsResult(BenerailBaseModel):
    authorizations: list[RcodeAuthorization] | None = None
    field_links: LinksUnderscoreType | None = Field(None, alias="_links")


class PlacesResult(BenerailBaseModel):
    places: list[PlaceResult] | None = None
    field_links: LinksUnderscoreType | None = Field(None, alias="_links")
