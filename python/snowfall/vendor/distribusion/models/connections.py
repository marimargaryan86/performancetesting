from typing import Any

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class SeatStation(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str


class FareClassesRelCode(DistribusionBaseModel):
    code: str | None
    identifier: str = pydantic.Field(..., alias="id")


class FaresRelFareClassPrice(DistribusionBaseModel):
    fare_class: FareClassesRelCode | None
    identifier: str = pydantic.Field(..., alias="id")
    price: int | None


class City(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    name: str | None


class Station(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str
    description: str | None
    latitude: float
    longitude: float
    name: str | None
    street_and_number: str | None
    time_zone: str
    zip_code: str | None
    area: Any | None
    city: City | None


class FareFeature(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    description: str | None
    name: str | None


class FareClass(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    iata_category: Any | None
    journey_type: str | None
    name: str | None
    fare_features: list[FareFeature] | None


class PassengerType(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str
    description: str
    max_age: int
    min_age: int
    name: str


class MarketingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    booking_fee: int | None
    code: str | None
    legal_name: str | None
    trade_name: str | None
    fare_classes: list[FareClass] | None
    passenger_types: list[PassengerType] | None


class OperatingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    legal_name: str | None
    trade_name: str | None


class VehicleType(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None


class Vehicle(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    vehicle_type: VehicleType | None


class Segment(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: str | None
    departure_time: str | None
    index: int | None
    arrival_station: Station
    departure_station: Station
    operating_carrier: OperatingCarrier | None
    vehicle: Vehicle | None


class Fare(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    price: int | None
    fare_class: FareClass | None


class Connection(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    electronic_ticket_available: bool | None
    arrival_time: str
    booked_out: bool | None
    cheapest_total_adult_price: int | None
    cheapest_fare_class_code: str | None
    departure_time: str
    duration: int | None
    arrival_station: Station
    departure_station: Station
    fares: list[FaresRelFareClassPrice] | None
    marketing_carrier: MarketingCarrier | None
    segments: list[Segment]
    currency: str


class ConnectionVacancy(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    total_price: int | None
    vacant: bool
    fees: dict[str, Any] | None
    currency: str


class Coordinates(DistribusionBaseModel):
    x: int | None  # noqa: WPS111
    y: int | None  # noqa: WPS111
    z: int | None  # noqa: WPS111


class Seat(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    coordinates: Coordinates | None
    fare_class: str | None
    label: str | None
    vacant: bool | None


class SeatsSegment(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: str | None
    departure_time: str | None
    index: int | None
    arrival_station: SeatStation | None
    departure_station: SeatStation | None


class Car(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    index: int | None
    seats: list[Seat] | None


class ConnectionSeat(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    segment: SeatsSegment
    cars: list[Car]
