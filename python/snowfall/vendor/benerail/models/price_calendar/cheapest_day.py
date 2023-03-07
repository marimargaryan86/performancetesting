import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.payment import Price


class CheapestDayPricesAvailabilityProbability(BenerailBaseModel):
    availability_value: str | None = pydantic.Field(..., alias="value")
    href: str | None


class CheapestDayPriceFlexibility(BenerailBaseModel):
    flexibility_value: str | None = pydantic.Field(..., alias="value")
    href: str | None


class CheapestDayPricesComfortClass(BenerailBaseModel):
    class_value: str | None = pydantic.Field(..., alias="value")
    href: str | None


class CheapestDayPricesPrices(BenerailBaseModel):
    availability_probability: CheapestDayPricesAvailabilityProbability | None
    flexibility: CheapestDayPriceFlexibility | None
    price: Price | None
    comfort_class: CheapestDayPricesComfortClass | None
    is_promo: bool | None
    registered_at: str | None


class CheapestDayPrices(BenerailBaseModel):
    prices_date: str | None
    prices: list[CheapestDayPricesPrices] | None
