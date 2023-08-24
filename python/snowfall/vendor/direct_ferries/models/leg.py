import datetime
from collections.abc import Sequence
from typing import Any

from pydantic import v1 as pydantic

from snowfall.vendor.direct_ferries import enums
from snowfall.vendor.direct_ferries.models import (
    base,
    operator,
    passenger,
    ship,
    vehicle,
)


class Gender(base.CamelCaseBaseModel):
    identifier: enums.Gender = pydantic.Field(..., alias="id")
    name: enums.Gender


class Accommodation(base.CamelCaseBaseModel):
    accommodation_id: int
    capacity: int
    description: str
    is_cabin: bool
    is_deck_space: bool
    is_seat: bool
    is_shared: bool
    price: float
    quantity: int
    availability: int
    gender: Gender
    message: str | None
    minimum_occupancy: int


class LegBase(base.CamelCaseBaseModel):
    is_return_leg: bool
    route_id: int
    departure_date_time: datetime.datetime
    passengers: Sequence[passenger.PassengerBase]


class Leg(LegBase):
    ticket_reference: str | None
    operator: operator.Operator | None
    route_name: str | None
    accommodation_message: str | None
    departure_port_name: str | None
    departure_port_id: int | None
    departure_port_code: str
    arrival_port_name: str | None
    arrival_port_id: int | None
    arrival_port_code: str
    arrival_date_time: datetime.datetime
    duration_minutes: int | None
    is_accommodation_compulsory: bool | None
    latest_check_in_minutes: int | None
    ship: ship.Ship | None
    vehicles: Sequence[vehicle.Vehicle] | None
    passengers: Sequence[passenger.Passenger]
    accommodations: Sequence[Accommodation]
    meals: Any | None
    pdf_url: str | None
    pets: Any | None
