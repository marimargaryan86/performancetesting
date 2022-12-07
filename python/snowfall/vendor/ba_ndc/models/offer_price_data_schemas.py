"""Contains offer ref data schemas."""
import datetime
import uuid

import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.offer_ref_data_schemas import OfferRefData


class OfferPriceData(BaseSchema, extra=pydantic.Extra.allow):
    """Offer Price data schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    expires_at: datetime.datetime = pydantic.Field(description="Offer expiration time")
    ref: OfferRefData = pydantic.Field(description="Offer ref data")
    ndc_data: str = pydantic.Field(description="OfferPrice NDC response in xml format")
