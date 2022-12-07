"""Contains offer ref data schemas."""
import uuid

import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema


class OrderData(BaseSchema, extra=pydantic.Extra.allow):
    """Order data schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    order_item_ids: dict[str, str] = pydantic.Field(description="Order item uuid -> id")
    ndc_data: str = pydantic.Field(description="Order NDC response in xml format")
