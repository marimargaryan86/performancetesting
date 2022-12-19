from snowfall.vendor.karhoo.models.base import KarhooBaseModel


class Net(KarhooBaseModel):
    high: int | None
    low: int | None


class Price(KarhooBaseModel):
    currency_code: str | None
    high: int | None
    low: int | None
    net: Net | None


class Breakdown(KarhooBaseModel):
    value: int  # noqa: WPS110
    name: str
    description: str | None


class Fare(KarhooBaseModel):
    total: int
    currency: str
    gratuity_percent: int | None
    breakdown: list[Breakdown]
