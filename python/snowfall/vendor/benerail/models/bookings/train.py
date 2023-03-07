from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import ResourceLink


class TrainType1(BenerailBaseModel):
    href: str | None
    train_type_value: str | None = pydantic.Field(..., alias="value")


class TrainType(BenerailBaseModel):
    train_type: str | None
    preference_type: Literal["REQUIRED", "UNACCEPTABLE"] | None


class SeatDetails(BenerailBaseModel):
    href: str | None
    seat_details_value: str | None = pydantic.Field(..., alias="value")


class SpaceDetails(BenerailBaseModel):
    href: str | None
    space_details_value: str | None = pydantic.Field(..., alias="value")


class Flexibility(BenerailBaseModel):
    href: str | None
    flexibility_value: str | None = pydantic.Field(..., alias="value")


class Seat(BenerailBaseModel):
    seat_number: str | None
    seat_details: list[SeatDetails] | None


class ReservationDetails(BenerailBaseModel):
    placement_type: Literal["passengers", "bicycles"] | None
    coach: str | None
    space_details: list[SpaceDetails] | None
    seats: list[Seat] | None


class Admission(BenerailBaseModel):
    reservations: list[ResourceLink] | None
    is_reservation_required: bool
    validity_start_date: str | None
    validity_end_date: str | None


class Reservation(BenerailBaseModel):
    optionality: Literal["REQUIRED_RES", "OPTIONAL_RES"] | None
    overbooking: bool | None
    departure_date_time: str | None
    arrival_date_time: str | None
    train_type: TrainType | None
    train_numbers: list[str] | None
    reservation_details: ReservationDetails
    admission: ResourceLink
