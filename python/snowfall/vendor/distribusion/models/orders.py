from typing import Any, Optional

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class OrderCreateResponse(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    state: str
    created_at: str


class OrderResponse(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    state: str
    executed_at: Optional[str]
    created_at: Optional[str]
    booking: Optional[Any]
