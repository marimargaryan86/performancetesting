from pydantic import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import LinkToBinary, LinkToRcode


class Document(BenerailBaseModel):
    medium: LinkToRcode | None = None
    document_type: LinkToRcode | None = Field(None, alias="type")
    download_link: LinkToBinary | None = None


class TicketBookingState(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:itti:ticket_booking_state:PENDING",
    )
    ticket_booking_state_value: ConstrainedStr | None = Field(
        None,
        example="urn:itti:ticket_booking_state:PENDING",
        alias="value",
        regex="^urn:[a-z]*:ticket_booking_state:[A-Z]*$",
    )


class TicketFulfillmentState(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example=(
            "https://api.example.com/places/urn:itti:ticket_fulfillment_state:PENDING"
        ),
    )
    ticket_fulfillment_state_value: ConstrainedStr | None = Field(
        None,
        example="urn:itti:ticket_fulfillment_state:PENDING",
        alias="value",
        regex="^urn:[a-z]*:ticket_fulfillment_state:[A-Z]*$",
    )
