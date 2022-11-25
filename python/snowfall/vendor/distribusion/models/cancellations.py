from typing import Any, Dict, Optional

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class CancellationCondition(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    allowed: Optional[bool] = None
    cutoff: Optional[str] = None
    fee: Optional[int] = None
    deductions: Optional[Dict[str, Any]] = None


class Cancellation(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    created_at: Optional[str] = None
    fee: Optional[int] = None
    total_price: Optional[int] = None
    total_refund: Optional[int] = None
