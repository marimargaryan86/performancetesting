from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class BasicRateResponse(CamelCaseBaseModel):
    buy_currency: str
    sell_currency: str
    rate: float
