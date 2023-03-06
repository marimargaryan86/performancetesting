import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import ResourceLink


class Fulfillment(BenerailBaseModel):
    control_number: str
    fulfillment_state: str
    aftersales_state: str
    document: str


class Booking(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    dialogue_id: str | None
    dnr: str | None
    orders: list[ResourceLink] | None
    fulfillments: list[ResourceLink] | None


class ConfirmationEmail(BenerailBaseModel):
    email_tos: list[str] | None
    email_ccs: list[str] | None
    email_bccs: list[str] | None
    language: str | None
