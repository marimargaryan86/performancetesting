from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.booking import BookingInformation
from snowfall.vendor.benerail.models.bookings.payment import Price
from snowfall.vendor.benerail.models.link import RcodeLink, ResourceLink


class BookedOffer(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    order_id: str | None
    selected_offer_id: str | None
    status: Literal["SELECTED", "PREBOOKED", "BOOKED"] | None
    price: Price | None
    booking_information: BookingInformation | None
    booked_offer_parts: list[ResourceLink] | None
    booked_passengers: list[ResourceLink] | None
    booked_trips: list[ResourceLink] | None


class SelectedOfferPart(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    included: bool | None
    offer_part: ResourceLink | None
    available_booking_options: list[RcodeLink] | None
    selected_booking_options: list[RcodeLink] | None
    is_required_in_offer: bool | None


class SelectedOffer(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    offer: ResourceLink | None
    selected_offer_parts: list[ResourceLink] | None


class SelectedOfferPartIdBody(BenerailBaseModel):
    included: bool | None
    selected_booking_options: list[str] | None


class SelectedOffersBody(BenerailBaseModel):
    offer_id: str
