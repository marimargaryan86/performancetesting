import pydantic

from snowfall.vendor.payment.models.base import CamelCaseBaseModel


class ContactRequest(CamelCaseBaseModel):
    account_id: str
    first_name: str
    last_name: str
    email_address: str
    phone_number: str


class ContactResponse(CamelCaseBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    first_name: str
    last_name: str
    email_address: str
    phone_number: str
