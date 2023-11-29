from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.booking import BookingInformation
from snowfall.vendor.benerail.models.bookings.enums import BookedOfferStatus
from snowfall.vendor.benerail.models.bookings.payment import Price
from snowfall.vendor.benerail.models.link import RcodeLink, ResourceLink
from snowfall.vendor.benerail.models.trip_offers.link import OfferPartResourceLink


class BookedOffer(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    order_id: str | None = None
    selected_offer_id: str | None = None
    status: BookedOfferStatus | None = None
    price: Price | None = None
    booking_information: BookingInformation | None = None
    booked_offer_parts: list[ResourceLink] | None = None
    booked_passengers: list[ResourceLink] | None = None
    booked_trips: list[ResourceLink] | None = None


class SelectedOfferPart(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    included: bool | None = None
    offer_part: ResourceLink | None = None
    available_booking_options: list[RcodeLink] | None = None
    selected_booking_options: list[RcodeLink] | None = None
    is_required_in_offer: bool | None = None


class SelectedOffer(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    offer: ResourceLink | None = None
    selected_offer_parts: list[ResourceLink] | None = None


class SelectedOfferPartIdBody(BenerailBaseModel):
    included: bool | None = None
    selected_booking_options: list[str] | None = None


class SelectedOffersBody(BenerailBaseModel):
    offer_id: str


class RefundOffer(BenerailBaseModel):
    identifier: str = Field(..., alias="id")
    state: str | None = None
    total_original_amount: Price | None = None
    total_refund_amount: Price | None = None
    refund_offer_parts: list[OfferPartResourceLink] | None = None
