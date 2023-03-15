from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.price_calendar.cheapest_day import (
    CheapestDayPrices,
)


class PriceCalendarsResultRequestParamsOrigin(BenerailBaseModel):
    param_value: str | None = Field(
        None,
        example="urn:bnds:tstatn_id:BEBMI",
        alias="value",
    )
    href: str | None = Field(
        None,
        example="https://api.example.com/locations/XyR54p...",
    )


class PriceCalendarsResultRequestParamsDestination(BenerailBaseModel):
    param_value: str | None = Field(
        None,
        example="urn:bnds:tstatn_id:FRPNO",
        alias="value",
    )
    href: str | None = Field(
        None,
        example="https://api.example.com/locations/XyR54p...",
    )


class PriceCalendarsResultRequestParameters(BenerailBaseModel):
    from_date: str | None = Field(None, example="2021-10-20")
    period: str | None = Field(
        None,
        example="P1M",
    )
    origin: PriceCalendarsResultRequestParamsOrigin | None = None
    destination: PriceCalendarsResultRequestParamsDestination | None = None


class PriceCalendarsResultLinks(BenerailBaseModel):
    link_self: str | None = Field(
        None,
        description="return this",
        example="https://api.example.com/price-calendars?origin=urn:bnds:tstatn_id:BEBMI&destination=urn:bnds:tstatn_id:FRPNO&from-date=2021-10-20&period=P1M",
        alias="self",
    )
    next_page: str | None = Field(
        None,
        description="return next period similar to this",
        example="https://api.example.com/price-calendars?origin=urn:bnds:tstatn_id:BEBMI&destination=urn:bnds:tstatn_id:FRPNO&from-date=2021-11-20&period=P1M",
        alias="next",
    )
    previous_page: str | None = Field(
        None,
        description="return previous period similar to this",
        example="https://api.example.com/price-calendars?origin=urn:bnds:tstatn_id:BEBMI&destination=urn:bnds:tstatn_id:FRPNO&from-date=2021-09-20&period=P1M",
        alias="previous",
    )


class PriceCalendarsResult(BenerailBaseModel):
    request_parameters: PriceCalendarsResultRequestParameters | None = None
    cheapest_day_prices: list[CheapestDayPrices] | None = None
    links: PriceCalendarsResultLinks | None = None
