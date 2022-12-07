"""Contains service ref data schemas."""
import datetime
import uuid

import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.seat_ref_data_schemas import IdMapping


class ServiceData(BaseSchema, extra=pydantic.Extra.allow):
    """Service data schema."""

    offer_id: uuid.UUID | None = pydantic.Field(description="Offer id")
    order_id: uuid.UUID | None = pydantic.Field(description="Order id")
    expires_at: datetime.datetime = pydantic.Field(description="Offer expiration time")
    item_ids: list[IdMapping] = pydantic.Field(description="offer item id mapping")
    ndc_data: str = pydantic.Field(description="Service NDC response in xml format")
