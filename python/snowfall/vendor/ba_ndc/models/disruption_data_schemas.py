"""Contains disruption data schemas."""
import uuid

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema


class DisruptionData(BaseSchema, extra=pydantic.Extra.allow):
    """Order data schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    pnr: str = pydantic.Field(description="order pnr")
    ndc_data: str = pydantic.Field(description="Disruption response in xml format")
