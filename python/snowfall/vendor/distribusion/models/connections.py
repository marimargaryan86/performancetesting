from typing import Any, Dict, List

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
    code: str | None
    description: str | None
    latitude: float | None
    longitude: float | None
    name: str | None
    street_and_number: str | None
    time_zone: str | None
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
    fare_features: List[FareFeature] | None


class PassengerType(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    description: str | None
    max_age: int | None
    min_age: int | None
    name: str | None


class MarketingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    booking_fee: int | None
    code: str | None
    legal_name: str | None
    trade_name: str | None
    fare_classes: List[FareClass] | None
    passenger_types: List[PassengerType] | None


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
    arrival_station: Station | None
    departure_station: Station | None
    operating_carrier: OperatingCarrier | None
    vehicle: Vehicle | None


class Fare(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    price: int | None
    fare_class: FareClass | None


class Connection(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    electronic_ticket_available: bool | None
    arrival_time: str | None
    booked_out: bool | None
    cheapest_total_adult_price: int | None
    cheapest_fare_class_code: str | None
    departure_time: str | None
    duration: int | None
    arrival_station: Station | None
    departure_station: Station | None
    fares: List[FaresRelFareClassPrice] | None
    marketing_carrier: MarketingCarrier | None
    segments: List[Segment] | None


class ConnectionVacancy(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    total_price: int | None
    vacant: bool | None
    fees: Dict[str, Any] | None


class Coordinates(DistribusionBaseModel):
    x: int | None
    y: int | None
    z: int | None


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
    seats: List[Seat] | None


class ConnectionSeat(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    segment: SeatsSegment
    cars: list[Car]
