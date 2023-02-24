import datetime
from typing import Any, Optional, Sequence

import pydantic

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
    message: Optional[str]
    minimum_occupancy: int


class LegBase(base.CamelCaseBaseModel):
    is_return_leg: bool
    route_id: str
    departure_date_time: datetime.datetime
    passengers: Sequence[passenger.PassengerBase]


class Leg(LegBase):
    ticket_reference: Optional[str]
    operator: Optional[operator.Operator]
    route_name: Optional[str]
    accommodation_message: Optional[str]
    departure_port_name: Optional[str]
    departure_port_id: Optional[int]
    departure_port_code: str
    arrival_port_name: Optional[str]
    arrival_port_id: Optional[int]
    arrival_port_code: str
    arrival_date_time: Optional[datetime.datetime]
    duration_minutes: Optional[int]
    is_accommodation_compulsory: Optional[bool]
    latest_check_in_minutes: Optional[int]
    ship: Optional[ship.Ship]
    vehicles: Optional[Sequence[vehicle.Vehicle]]
    passengers: Sequence[passenger.Passenger]
    accommodations: Sequence[Accommodation]
    meals: Optional[Any]
    pdf_url: Optional[str]
    pets: Optional[Any]
