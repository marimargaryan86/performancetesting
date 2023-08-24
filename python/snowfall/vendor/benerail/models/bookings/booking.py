from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.enums import Direction, LegType
from snowfall.vendor.benerail.models.bookings.payment import Price
from snowfall.vendor.benerail.models.bookings.ticket import (
    Document,
    TicketBookingState,
    TicketFulfillmentState,
)
from snowfall.vendor.benerail.models.bookings.train import (
    Admission,
    Flexibility,
    Reservation,
)
from snowfall.vendor.benerail.models.link import RcodeLink, ResourceLink
from snowfall.vendor.benerail.models.place import Place
from snowfall.vendor.benerail.models.products.product import ComfortClass


class Fulfillment(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    control_number: str | None = None
    control_number_type: str | None = None
    title: str | None = None
    fulfillment_state: TicketFulfillmentState | None = None
    booking_state: TicketBookingState | None = None
    provisional_aftersales_state: RcodeLink | None = None
    aftersales_state: RcodeLink | None = None
    stock_control_number: str | None = None
    price: Price | None = None
    issue_language: str | None = None
    documents: list[Document] | None = None


class Booking(BenerailBaseModel):
    identifier: str = Field(..., alias="id")
    dialogue_id: str
    dnr: str
    orders: list[ResourceLink] | None = None
    fulfillments: list[ResourceLink] | None = None


class ConfirmationEmail(BenerailBaseModel):
    email_tos: list[str] | None = None
    email_ccs: list[str] | None = None
    email_bccs: list[str] | None = None
    language: str | None = Field(None, description="ISO Language code", example="EN")


class BookedTripLeg(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    booked_offer_trip_id: str | None = None
    leg_type: LegType | None = None
    duration: str | None = Field(
        None,
        description="Overall duration of the trip",
        example="PT20M",
    )
    origin: Place | None = None
    destination: Place | None = None
    departure_at: str | None = Field(
        None,
        description="ISO-8601 timestamp showing date time and timezone of departure",
        example="2021-09-29T13:20:34.143+02:00",
    )
    arrival_at: str | None = Field(
        None,
        description="ISO-8601 timestamp showing date time and timezone of arrival",
        example="2021-09-29T13:20:34.143+02:00",
    )


class BookedTrip(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    booked_offer_id: str | None = None
    duration: str | None = Field(
        None,
        description="Overall duration of the trip",
        example="PT20M",
    )
    origin: Place | None = None
    destination: Place | None = None
    departure_at: str | None = Field(
        None,
        description="ISO-8601 timestamp showing date time and timezone of departure",
        example="2021-09-29T13:20:34.143+02:00",
    )
    arrival_at: str | None = Field(
        None,
        description="ISO-8601 timestamp showing date time and timezone of arrival",
        example="2021-09-29T13:20:34.143+02:00",
    )
    direction: Direction | None = None
    hafas_reference: str | None = None


class BookedOfferPartCommon(BenerailBaseModel):
    origin: Place | None = None
    destination: Place | None = None
    price: Price | None = None
    flexibility: Flexibility | None = None
    comfort_class: ComfortClass | None = None
    product: ResourceLink | None = None
    passengers: list[ResourceLink] | None = None
    trip_leg_sequence: int | None = None


class BookedOfferPart(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    booked_offer_id: str | None = None
    offer_part_common: BookedOfferPartCommon | None = None
    offer_part_specific: Reservation | Admission | None = None


class BookingInformation(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    booked_offer_id: str | None = None
    provisional_balance: float | None = None
