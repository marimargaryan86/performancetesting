from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.enumeration.results import (
    AttributesResult,
    AttributeTypesResult,
    AuthorizationGroupsResult,
    AuthorizationsResult,
    PlacesResult,
    RcodesResult,
    TypesResult,
)
from snowfall.vendor.benerail.models.metadata import Metadata


class PlacesResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: PlacesResult | None = Field(None, alias="result")


class RcodesResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: RcodesResult = Field(..., alias="result")


class TypesResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: TypesResult | None = Field(None, alias="result")


class AttributesResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: AttributesResult | None = Field(None, alias="result")


class AuthorizationsResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: AuthorizationsResult | None = Field(None, alias="result")


class AttributeTypesResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: AttributeTypesResult | None = Field(None, alias="result")


class AuthorizationGroupsResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: AuthorizationGroupsResult | None = Field(None, alias="result")
