from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.enums import Severity
from snowfall.vendor.benerail.models.bookings.payment import Price
from snowfall.vendor.benerail.models.bookings.train import Flexibility
from snowfall.vendor.benerail.models.products.product import ComfortClass
from snowfall.vendor.benerail.models.trip_offers.features import Admission, Reservation
from snowfall.vendor.benerail.models.trip_offers.link import (
    OfferPartResourceLink,
    PassengerResourceLink,
    ProductResourceLink,
    TripResourceLink,
)


class Offer(BenerailBaseModel):
    identifier: str = Field(..., alias="id")
    offer_parts: list[OfferPartResourceLink]
    price: Price
    flexibility: Flexibility | None = None
    comfort_class: ComfortClass | None = None
    trip: TripResourceLink
    passengers: list[PassengerResourceLink]


class OfferPartCommon(BenerailBaseModel):
    optional: bool | None = None
    price: Price | None = None
    flexibility: Flexibility | None = None
    comfort_class: ComfortClass | None = None
    product: ProductResourceLink | None = None
    passengers: list[PassengerResourceLink] | None = None
    trip_leg_sequence: int | None = None
    is_required_in_offer: bool | None = None


class OfferPart(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    offer_part_common: OfferPartCommon | None = None
    offer_part_specific: Reservation | Admission | None = None


class Message(BenerailBaseModel):
    severity: Severity | None = None
    message: str | None = None
