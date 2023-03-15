from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.payment import Price


class CheapestDayPricesAvailabilityProbability(BenerailBaseModel):
    cheapest_value: str | None = Field(
        None,
        example="urn:bnds:availability_probability:LIKELY",
        alias="value",
    )
    href: str | None = Field(
        None,
        example="https://api.example.com/rcode/XyR545g...",
    )


class CheapestDayPricesFlexibility(BenerailBaseModel):
    cheapest_value: str | None = Field(
        None,
        example="urn:bnds:railteam_flexibility:NF",
        alias="value",
    )
    href: str | None = Field(
        None,
        example="https://api.example.com.com/rcode/XyR574g...",
    )


class CheapestDayPricesComfortClass(BenerailBaseModel):
    cheapest_value: str | None = Field(
        None,
        example="urn:bnds:comfort-class:2",
        alias="value",
    )
    href: str | None = Field(
        None,
        example="https://api.example.com/rcode/XyR474g...",
    )


class CheapestDayPricesPrices(BenerailBaseModel):
    availability_probability: CheapestDayPricesAvailabilityProbability | None = None
    flexibility: CheapestDayPricesFlexibility | None = None
    price: Price | None = None
    comfort_class: CheapestDayPricesComfortClass | None = None
    is_promo: bool | None = Field(
        None,
        description="Indicater for promotional character of price.",
        example=False,
    )
    registered_at: str | None = Field(
        None,
        description="Time when registered in BeNe database.",
        example="2021-03-29T08:08:32.852+02:00",
    )


class CheapestDayPrices(BenerailBaseModel):
    prices_date: str | None = Field(
        None,
        description="Day for which cheapest prices are returned",
        example="2021-10-20",
    )
    prices: list[CheapestDayPricesPrices] | None = None
