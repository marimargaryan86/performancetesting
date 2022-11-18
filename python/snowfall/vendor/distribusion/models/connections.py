from typing import Any, Dict, List, Optional

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class SeatStation(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str


class FareClassesRelCode(DistribusionBaseModel):
    code: Optional[str] = None
    identifier: str = pydantic.Field(..., alias="id")


class FaresRelFareClassPrice(DistribusionBaseModel):
    fare_class: Optional[FareClassesRelCode] = None
    identifier: str = pydantic.Field(..., alias="id")
    price: Optional[int] = None


class City(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    name: Optional[str] = None


class Station(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    name: Optional[str] = None
    street_and_number: Optional[str] = None
    time_zone: Optional[str] = None
    zip_code: Optional[str] = None
    area: Optional[Any] = None
    city: Optional[City] = None


class FareFeature(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None


class FareClass(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    iata_category: Optional[Any] = None
    journey_type: Optional[str] = None
    name: Optional[str] = None
    fare_features: Optional[List[FareFeature]] = None


class PassengerType(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    max_age: Optional[int] = None
    min_age: Optional[int] = None
    name: Optional[str] = None


class MarketingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    booking_fee: Optional[int] = None
    code: Optional[str] = None
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    fare_classes: Optional[List[FareClass]] = None
    passenger_types: Optional[List[PassengerType]] = None


class OperatingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None


class VehicleType(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None


class Vehicle(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    vehicle_type: Optional[VehicleType] = None


class Segment(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    index: Optional[int] = None
    arrival_station: Optional[Station] = None
    departure_station: Optional[Station] = None
    operating_carrier: Optional[OperatingCarrier] = None
    vehicle: Optional[Vehicle] = None


class Fare(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    price: Optional[int] = None
    fare_class: Optional[FareClass] = None


class Connection(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    electronic_ticket_available: Optional[bool] = None
    arrival_time: Optional[str] = None
    booked_out: Optional[bool] = None
    cheapest_total_adult_price: Optional[int] = None
    cheapest_fare_class_code: Optional[str] = None
    departure_time: Optional[str] = None
    duration: Optional[int] = None
    arrival_station: Optional[Station] = None
    departure_station: Optional[Station] = None
    fares: Optional[List[FaresRelFareClassPrice]] = None
    marketing_carrier: Optional[MarketingCarrier] = None
    segments: Optional[List[Segment]] = None


class ConnectionVacancy(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    total_price: Optional[int] = None
    vacant: Optional[bool] = None
    fees: Optional[Dict[str, Any]] = None


class Coordinates(DistribusionBaseModel):
    x: Optional[int] = None
    y: Optional[int] = None
    z: Optional[int] = None


class Seat(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    fare_class: Optional[str] = None
    label: Optional[str] = None
    vacant: Optional[bool] = None


class SeatsSegment(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    index: Optional[int] = None
    arrival_station: Optional[SeatStation] = None
    departure_station: Optional[SeatStation] = None


class Car(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    index: Optional[int] = None
    seats: Optional[List[Seat]] = None


class ConnectionSeat(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    segment: SeatsSegment
    cars: list[Car]
