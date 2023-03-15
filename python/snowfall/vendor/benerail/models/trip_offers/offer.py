from pydantic import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.enums import Optionality, Severity
from snowfall.vendor.benerail.models.bookings.payment import Price
from snowfall.vendor.benerail.models.bookings.train import Flexibility
from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.products.product import ComfortClass


class Offer(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    offer_parts: list[ResourceLink]
    price: Price | None = None
    flexibility: Flexibility | None = None
    comfort_class: ComfortClass | None = None
    trip: ResourceLink
    passengers: list[ResourceLink]


class Reservation(BenerailBaseModel):
    reservation_type: str | None = Field(
        None,
        description="reservation",
        example="reservation",
        alias="type",
    )
    admission: ResourceLink | None = None
    optionality: Optionality | None = None


class Admission(BenerailBaseModel):
    admission_type: str | None = Field(
        None,
        description="admission",
        example="admission",
        alias="type",
    )
    reservations: list[ResourceLink] | None = None
    is_reservation_required: bool | None = None


class OfferPartCommon(BenerailBaseModel):
    optional: bool | None = None
    price: Price | None = None
    flexibility: Flexibility | None = None
    comfort_class: ComfortClass | None = None
    product: ResourceLink | None = None
    passengers: list[ResourceLink] | None = None
    trip_leg_sequence: int | None = None
    is_required_in_offer: bool | None = None


class OfferPart(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    offer_part_common: OfferPartCommon | None = None
    offer_part_specific: Reservation | Admission | None = None


class Message(BenerailBaseModel):
    severity: Severity | None = None
    message: str | None = None


class BookableStatus(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:bnds:bookable_status:BOOKABLE",
    )
    status_value: ConstrainedStr | None = Field(
        None,
        example="urn:bnds:bookable_status:BOOKABLE",
        alias="value",
        regex="^urn:[a-z]*:bookable_status:[A-Z_]*$",
    )
