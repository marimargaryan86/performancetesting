import datetime
from enum import Enum

import pydantic

from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class Account(CamelCaseBaseModel):
    account_name: str
    legal_entity_type: str = "company"
    street: str
    city: str
    country: str
    postal_code: str | None
    state_or_province: str | None
    spread_table: str = "flat_0.00"
    api_trading: bool = True
    online_trading: bool = True
    phone_trading: bool = True
    terms_and_conditions_accepted: bool | None = True


class AccountRequest(Account):
    """account request pydantic model."""


class StatusEnum(Enum):
    enabled = "enabled"
    enabled_no_trading = "enabled_no_trading"
    disabled = "disabled"


class AccountUpdateRequest(CamelCaseBaseModel):
    status: StatusEnum = StatusEnum.enabled
    account_name: str | None = None
    legal_entity_type: str | None = None
    street: str | None = None
    city: str | None = None
    country: str | None = None
    postal_code: str | None = None
    state_or_province: str | None = None
    spread_table: str | None = None
    api_trading: bool | None = None
    online_trading: bool | None = None
    phone_trading: bool | None = None
    terms_and_conditions_accepted: bool | None = None


class AccountResponse(Account):
    identifier: str = pydantic.Field(..., alias="id")
    updated_at: datetime.datetime
    status: StatusEnum
