import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.price_calendar.cheapest_day import (
    CheapestDayPrices,
)


class PriceCalendarsResultRequestParametersOrigin(BenerailBaseModel):
    param_value: str | None = pydantic.Field(..., alias="value")
    href: str | None


class PriceCalendarsResultRequestParamsDestination(BenerailBaseModel):
    param_value: str | None = pydantic.Field(..., alias="value")
    href: str | None


class PriceCalendarsResultRequestParameters(BenerailBaseModel):
    from_date: str | None
    period: str | None
    origin: PriceCalendarsResultRequestParametersOrigin | None
    destination: PriceCalendarsResultRequestParamsDestination | None


class PriceCalendarsResultLinks(BenerailBaseModel):
    self_string: str | None
    next_page: str | None = pydantic.Field(..., alias="next")
    previous: str | None


class PriceCalendarsResult(BenerailBaseModel):
    request_parameters: PriceCalendarsResultRequestParameters | None
    cheapest_day_prices: list[CheapestDayPrices] | None
    links: PriceCalendarsResultLinks | None
