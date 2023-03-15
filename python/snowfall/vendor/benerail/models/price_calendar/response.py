from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.metadata import Metadata
from snowfall.vendor.benerail.models.price_calendar.price_calendar import (
    PriceCalendarsResult,
)


class PriceCalendarsResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: PriceCalendarsResult | None = Field(None, alias="result")
