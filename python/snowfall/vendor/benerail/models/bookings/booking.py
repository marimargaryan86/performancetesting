import datetime
from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
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
    identifier: str | None = pydantic.Field(..., alias="id")
    control_number: str | None
    control_number_type: str | None
    title: str | None
    fulfillment_state: TicketFulfillmentState | None
    booking_state: TicketBookingState | None
    provisional_aftersales_state: RcodeLink | None
    aftersales_state: RcodeLink | None
    stock_control_number: str | None
    price: Price | None
    issue_language: str | None
    documents: list[Document] | None


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


class BookedTripLeg(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    booked_offer_trip_id: str | None
    leg_type: Literal["TIMED", "TRANSFER"] | None
    duration: str | None
    origin: Place | None
    destination: Place | None
    departure_at: datetime.datetime | None
    arrival_at: datetime.datetime | None


class BookedTrip(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    booked_offer_id: str | None
    duration: str | None
    origin: Place | None
    destination: Place | None
    departure_at: datetime.datetime | None
    arrival_at: datetime.datetime | None
    direction: Literal[
        "single-travel",
        "outward-travel",
        "return-travel",
        "roundtrip-travel",
    ] | None
    hafas_reference: str | None


class BookedOfferPartCommon(BenerailBaseModel):
    origin: Place | None
    destination: Place | None
    price: Price | None
    flexibility: Flexibility | None
    comfort_class: ComfortClass | None
    product: ResourceLink | None
    passengers: list[ResourceLink] | None
    trip_leg_sequence: int | None


class BookedOfferPart(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    booked_offer_id: str | None
    offer_part_common: BookedOfferPartCommon | None
    offer_part_specific: Reservation | Admission | None


class BookingInformation(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    booked_offer_id: str | None
    provisional_balance: int | None
