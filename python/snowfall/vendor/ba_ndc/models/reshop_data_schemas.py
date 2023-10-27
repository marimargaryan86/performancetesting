"""Contains offer ref data schemas."""

import uuid

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema


class ReshopData(BaseSchema, extra=pydantic.Extra.allow):
    """Reshop data schema."""

    order_id: uuid.UUID = pydantic.Field(description="Order id")
    offer_ids: dict[str, str] = pydantic.Field(description="Offer uuid -> id")
    ndc_data: str = pydantic.Field(
        description="Order Reshop NDC response in xml format",
    )
