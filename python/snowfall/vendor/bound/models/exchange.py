from snowfall.vendor.bound.models.base import CamelCaseBaseModel


class PriceCurrency(CamelCaseBaseModel):
    price: int
    currency: str


class Quote(CamelCaseBaseModel):
    amount: int
    buy_currency: str
    sell_currency: str
    rate: float


class Rate(CamelCaseBaseModel):
    buy_currency: str
    sell_currency: str
    rate: float
