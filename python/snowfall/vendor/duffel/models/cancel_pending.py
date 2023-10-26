from __future__ import annotations

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel


class CancelData(DuffelBaseModel):
    refund_to: str
    refund_currency: str
    refund_amount: str
    order_id: str
    live_mode: bool
    identifier: str = pydantic.Field(alias="id")
    expires_at: str | None
    created_at: str
    confirmed_at: str | None


class CancelResponse(DuffelBaseModel):
    response_data: CancelData = pydantic.Field(alias="data")
