from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.metadata import MetaData
from snowfall.vendor.benerail.models.price_calendar.price_calendar import (
    PriceCalendarsResult,
)


class PriceCalendarsResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: PriceCalendarsResult | None
