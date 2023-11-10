import datetime
from enum import Enum

from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class BasicRateResponse(CamelCaseBaseModel):
    buy_currency: str
    sell_currency: str
    rate: float


class ConversionDatePreferenceEnum(Enum):
    earliest = "earliest"
    next_day = "next_day"
    default = "default"
    optimize_liquidity = "optimize_liquidity"


class FixedSideEnum(Enum):
    buy = "buy"
    sell = "sell"


class DetailedRateRequest(CamelCaseBaseModel):
    sell_currency: str
    buy_currency: str
    fixed_side: FixedSideEnum
    amount: str
    on_behalf_of: str | None = None
    conversion_date: datetime.date | None = None
    conversion_date_preference: ConversionDatePreferenceEnum | None = None


class DetailedRateResponse(CamelCaseBaseModel):
    settlement_cut_off_time: datetime.datetime | None = None
    currency_pair: str | None = None
    client_buy_currency: str
    client_sell_currency: str
    client_buy_amount: str
    client_sell_amount: str | None = None
    fixed_side: FixedSideEnum = FixedSideEnum.buy
    client_rate: str | None = None
