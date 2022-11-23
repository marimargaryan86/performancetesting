from snowfall.vendor.apilayer.models.base import CamelCaseBaseModel


class Quote(CamelCaseBaseModel):
    amount: int
    buy_currency: str
    sell_currency: str
    rate: float


class Rate(CamelCaseBaseModel):
    buy_currency: str
    sell_currency: str
    rate: float
