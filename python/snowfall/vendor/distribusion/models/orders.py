from typing import Any, Dict, List, Optional

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class FareFeature(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None


class Passenger(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    serial_code: Optional[Any] = None


class SegmentPassenger(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    seat_number: Optional[Any] = None
    passenger: Optional[Passenger] = None


class Segment(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    index: Optional[int] = None
    segment_passengers: Optional[List[SegmentPassenger]] = None


class FareClass(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    iata_category: Optional[Any] = None
    journey_type: Optional[str] = None
    name: Optional[str] = None
    fare_features: Optional[List[FareFeature]] = None
    passenger_group_rules: Optional[List[Dict[str, Any]]] = None  # noqa: WPS234
    ticket_validity_rules: Optional[List[Dict[str, Any]]] = None  # noqa: WPS234


class Booking(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: Optional[str] = None
    connection_reference: Optional[Any] = None
    created_at: Optional[str] = None
    departure_time: Optional[str] = None
    distribusion_booking_number: Optional[str] = None
    duration: Optional[int] = None
    flight_number: Optional[Any] = None
    marketing_carrier_booking_number: Optional[str] = None
    pax: Optional[int] = None
    total_price: Optional[int] = None
    fare_class: Optional[FareClass] = None
    passengers: Optional[List[Passenger]] = None
    segments: Optional[List[Segment]] = None


class OrderCreateResponse(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    state: str
    created_at: str


class OrderResponse(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    state: str
    executed_at: Optional[str]
    created_at: Optional[str]
    booking: Optional[Booking]
