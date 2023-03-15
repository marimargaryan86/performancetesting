from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.booking import ConfirmationEmail
from snowfall.vendor.benerail.models.dialogue.enums import OnTicket
from snowfall.vendor.benerail.models.link import LinkToRcode
from snowfall.vendor.benerail.models.regex import NumberRegex, URNRegex


class CustomerInfoRequest(BenerailBaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    state: URNRegex | None = None
    customer_info_type: URNRegex | None = Field(
        None,
        alias="type",
    )
    contract_type: URNRegex | None = None
    contact_info: str | None = None
    customer_id: NumberRegex | None = None
    organisation_id: NumberRegex | None = None
    person_id: NumberRegex | None = None


class CustomerInfoResponse(BenerailBaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    state: LinkToRcode | None = None
    customer_info_type: LinkToRcode | None = Field(None, alias="type")
    contract_type: LinkToRcode | None = None
    contact_info: str | None = None
    customer_id: str | None = None
    organisation_id: str | None = None
    person_id: str | None = None


class BookerReference(BenerailBaseModel):
    customer_name: str | None = None
    customer_number: NumberRegex | None = None
    topo: str | None = None
    on_ticket: OnTicket | None = None


class BookerRequest(BenerailBaseModel):
    confirmation_email: ConfirmationEmail | None = None
    references: BookerReference | None = None
    crm_info: CustomerInfoRequest | None = None


class BookerResponse(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    references: BookerReference | None = None
    crm_info: CustomerInfoResponse | None = None
    confirmation_email: ConfirmationEmail | None = None
