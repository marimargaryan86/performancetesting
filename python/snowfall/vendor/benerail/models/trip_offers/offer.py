from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.payment import Price
from snowfall.vendor.benerail.models.bookings.train import Flexibility
from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.products.product import ComfortClass


class Offer(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    offer_parts: list[ResourceLink]
    price: Price | None
    flexibility: Flexibility | None
    comfort_class: ComfortClass | None
    trip: ResourceLink
    passenger: list[ResourceLink]


class Reservation(BenerailBaseModel):
    reservation_type: str | None = pydantic.Field(..., alias="type")
    admission: ResourceLink | None
    optionality: Literal["included", "mandatory", "optional"] | None


class Admission(BenerailBaseModel):
    admission_type: str | None = pydantic.Field(..., alias="type")
    reservations: list[ResourceLink] | None
    is_reservation_required: bool | None


class OfferPartCommon(BenerailBaseModel):
    optional: bool | None
    price: Price | None
    flexibility: Flexibility | None
    comfort_class: ComfortClass | None
    product: ResourceLink | None
    trip_leg_sequence: int | None
    is_required_in_offer: bool | None


class OfferPart(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    offer_part_common: OfferPartCommon | None
    offer_part_specific: Reservation | Admission | None


class Message(BenerailBaseModel):
    severity: Literal["error", "warning"] | None
    message: str | None


class BookableStatus(BenerailBaseModel):
    href: str | None
    status_value: str | None = pydantic.Field(..., alias="value")
