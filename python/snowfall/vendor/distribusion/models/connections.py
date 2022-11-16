from typing import Optional

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class Station(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str


class MarketingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")


class Segment(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    index: int
    departure_time: str
    arrival_time: str
    departure_station: Station
    arrival_station: Station


class FareClass(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str


class Fare(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    price: int
    fare_class: FareClass


class Connection(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    electronic_ticket_available: bool
    duration: int
    departure_time: str
    cheapest_total_adult_price: int
    cheapest_fare_class_code: str
    booked_out: bool
    arrival_time: str
    segments: list[Segment]
    marketing_carrier: MarketingCarrier
    fares: list[Fare]
    departure_station: Station
    arrival_station: Station


class ConnectionVacancy(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    vacant: bool
    total_price: int


class Coordinates(DistribusionBaseModel):
    x: int
    y: int
    z: int


class Seat(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str
    label: str
    fare_class: Optional[str]
    vacant: bool
    coordinates: Coordinates


class Car(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    index: int
    seats: list[Seat]


class ConnectionSeat(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    segment: Segment
    cars: list[Car]
