from pydantic import v1 as pydantic

from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class BalanceRequest(CamelCaseBaseModel):
    currency: str
    on_behalf_of: str


class BalanceResponse(CamelCaseBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    account_id: str
    currency: str
    amount: str
