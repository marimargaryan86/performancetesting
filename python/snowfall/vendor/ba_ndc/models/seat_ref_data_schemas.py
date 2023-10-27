"""Contains seat ref data schemas."""

import datetime
import uuid

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema


class IdMapping(BaseSchema):
    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    external_id: str = pydantic.Field(description="external id ")


class SeatRefData(BaseSchema, extra=pydantic.Extra.allow):
    """Seat reference data schema."""

    offer_id: uuid.UUID | None = pydantic.Field(description="Offer id")
    order_id: uuid.UUID | None = pydantic.Field(description="Order id")
    expires_at: datetime.datetime = pydantic.Field(
        description="Seat availability expiration time",
    )
    seat_ids: list[IdMapping] = pydantic.Field(description="Seat id mapping")
    ndc_data: str = pydantic.Field(
        description="SeatAvailability NDC response in xml format",
    )
