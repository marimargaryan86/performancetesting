from datetime import date

from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.enumeration.rcode_types import (
    RcodeAttributeAttributeType,
)


class RcodeAttributeValue(BenerailBaseModel):
    last_update_at: date | None = Field(None, example="2020-10-25")
    number_value: float | None = None
    boolean_value: bool | None = None
    string_value: str | None = None


class RcoderesultLabels(BenerailBaseModel):
    code_short: str | None = None
    code_long: str | None = None
    text: str | None = None


class RcodeMetaDataValidityTravel(BenerailBaseModel):
    starts_at: date | None = Field(None, example="2020-09-25")
    ends_at: date | None = Field(None, example="2020-10-25")


class RcodeMetaDataValidity(BenerailBaseModel):
    starts_at: date | None = Field(None, example="2022-09-25")
    travel: RcodeMetaDataValidityTravel | None = None


class RcodeMetaData(BenerailBaseModel):
    last_update_at: str | None = Field(None, example="25-09-2020T16:00:00Z")
    validity: RcodeMetaDataValidity | None = None


class RcodeAttribute(BenerailBaseModel):
    attribute_type: RcodeAttributeAttributeType | None = None
    attribute_values: dict[str, RcodeAttributeValue] | None = Field(
        None,
        alias="values",
    )
