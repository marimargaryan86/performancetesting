import pydantic

from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class BalanceResponse(CamelCaseBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    account_id: str
    currency: str
    amount: str
