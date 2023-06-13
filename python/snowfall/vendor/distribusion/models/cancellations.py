from typing import Any

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class CancellationCondition(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    allowed: bool | None = None
    cutoff: str | None = None
    fee: int | None = None
    deductions: dict[str, Any] | None = None


class Cancellation(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    created_at: str | None = None
    fee: int | None = None
    total_price: int | None = None
    total_refund: int | None = None
