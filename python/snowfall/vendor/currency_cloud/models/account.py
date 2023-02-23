import pydantic

from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class Account(CamelCaseBaseModel):
    account_name: str
    legal_entity_type: str = "company"
    street: str
    city: str
    state_or_province: str
    country: str
    postal_code: str
    spread_table: str = "flat_0.00"
    api_trading: bool = True
    online_trading: bool = False
    phone_trading: bool = True
    terms_and_conditions_accepted: bool = True


class AccountRequest(Account):
    """account request pydantic model."""


class AccountResponse(Account):
    identifier: str = pydantic.Field(..., alias="id")
