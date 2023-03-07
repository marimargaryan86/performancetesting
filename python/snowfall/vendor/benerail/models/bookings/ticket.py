import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import LinkToBinary, LinkToRcode


class Document(BenerailBaseModel):
    medium: LinkToRcode | None
    document_type: LinkToRcode | None = pydantic.Field(..., alias="type")
    download_link: LinkToBinary | None


class TicketBookingState(BenerailBaseModel):
    href: str | None
    booking_state_value: str | None = pydantic.Field(..., alias="value")


class TicketFulfillmentState(BenerailBaseModel):
    href: str | None
    fulfillment_state_value: str | None = pydantic.Field(..., alias="value")
