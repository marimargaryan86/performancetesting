from pydantic.v1 import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.enums import (
    Optionality,
    PlacementType,
    PreferenceType,
)
from snowfall.vendor.benerail.models.bookings.payment import FormOfPaymentURN
from snowfall.vendor.benerail.models.link import ResourceLink


class TrainType1(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:bnds:train_type:ICE",
    )
    train_type_value: ConstrainedStr | None = Field(
        None,
        example="urn:bnds:train_type:ICE",
        alias="value",
        regex="^urn:[a-z]*:train_type:[A-Z]*$",
    )


class TrainType(BenerailBaseModel):
    train_type: str | None = Field(None, example="urn:bdws:train_type:THA")
    preference_type: PreferenceType | None = None


class SeatDetails(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:itti:seat_details:W",
    )
    seat_details_value: FormOfPaymentURN | None = Field(None, alias="value")


class SpaceDetails(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:itti:space_details:C4",
    )
    space_details_value: ConstrainedStr | None = Field(
        None,
        example="urn:itti:space_details:C4",
        alias="value",
        regex="^urn:[a-z]*:space_details:[A-Z]*$",
    )


class Flexibility(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:bnds:railteam_flexibility:FF",
    )
    flexibility_value: ConstrainedStr | None = Field(
        None,
        example="urn:bnds:railteam_flexibility:FF",
        alias="value",
        regex="^urn:[a-z]*:railteam_flexibility:[A-Z]*$",
    )


class Seat(BenerailBaseModel):
    seat_number: str | None = None
    seat_details: list[SeatDetails] | None = None


class ReservationDetails(BenerailBaseModel):
    placement_type: PlacementType | None = None
    coach: str | None = None
    space_details: list[SpaceDetails] | None = None
    seats: list[Seat] | None = None


class Admission(BenerailBaseModel):
    reservations: list[ResourceLink] | None = None
    is_reservation_required: bool
    validity_start_date: str | None = None
    validity_end_date: str | None = None


class Reservation(BenerailBaseModel):
    optionality: Optionality | None = None
    overbooking: bool | None = None
    departure_date_time: str | None = None
    arrival_date_time: str | None = None
    train_type: TrainType | None = None
    train_numbers: list[str] | None = None
    reservation_details: ReservationDetails
    admission: ResourceLink
