from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.booking import ConfirmationEmail
from snowfall.vendor.benerail.models.link import LinkToRcode


class CustomerInfoRequest(BenerailBaseModel):
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    state: str | None
    customer_info_request_type: str | None = pydantic.Field(..., alias="type")
    contract_type: str | None
    contact_info: str | None
    customer_id: str | None
    organisation_id: str | None
    person_id: str | None


class CustomerInfoResponse(BenerailBaseModel):
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    state: LinkToRcode | None
    customer_info_response_type: LinkToRcode | None = pydantic.Field(..., alias="type")
    contract_type: LinkToRcode | None
    contact_info: str | None
    customer_id: str | None
    organisation_id: str | None
    person_id: str | None


class BookerReference(BenerailBaseModel):
    customer_name: str | None
    customer_number: str | None
    topo: str | None
    on_ticket: Literal["customerName", "customerNumber", "topo", "none"] | None


class BookerRequest(BenerailBaseModel):
    confirmation_email: ConfirmationEmail | None
    references: BookerReference | None
    crm_info: CustomerInfoRequest | None


class BookerResponse(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    references: BookerReference | None
    crm_info: CustomerInfoResponse | None
    confirmation_email: ConfirmationEmail | None
