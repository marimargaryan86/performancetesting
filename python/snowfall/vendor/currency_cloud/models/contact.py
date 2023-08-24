import re

from pydantic import v1 as pydantic

from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class ContactRequest(CamelCaseBaseModel):
    account_id: str
    first_name: str
    last_name: str
    email_address: str
    phone_number: str
    status: str = "enabled"


class ContactResponse(CamelCaseBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    first_name: str
    last_name: str
    email_address: str
    phone_number: str


def exclude_characters(contact_request: ContactRequest) -> None:
    pattern = re.compile("[<>]")
    contact_request.first_name = pattern.sub(
        "",
        contact_request.first_name,
    )
    contact_request.last_name = pattern.sub(
        "",
        contact_request.last_name,
    )
