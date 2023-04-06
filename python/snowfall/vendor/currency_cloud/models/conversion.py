import datetime

import pydantic

from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class ConversionRequest(CamelCaseBaseModel):
    buy_currency: str
    sell_currency: str
    amount: int
    reason: str
    fixed_side: str = "buy"
    term_agreement: str = "true"
    conversion_date_preference: str = "default"


class ConversionResponse(CamelCaseBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    settlement_date: datetime.datetime
    conversion_date: datetime.datetime
    client_buy_amount: str
    buy_currency: str
    sell_currency: str
    client_sell_amount: str
    core_rate: float
