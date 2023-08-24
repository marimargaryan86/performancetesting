from typing import Any

from pydantic import v1 as pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class FareFeature(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    description: str | None
    name: str | None


class Passenger(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    first_name: str | None
    last_name: str | None
    serial_code: Any | None


class SegmentPassenger(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    seat_number: Any | None
    passenger: Passenger | None


class Segment(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: str | None
    departure_time: str | None
    index: int | None
    segment_passengers: list[SegmentPassenger] | None


class FareClass(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    iata_category: Any | None
    journey_type: str | None
    name: str | None
    fare_features: list[FareFeature] | None
    passenger_group_rules: list[dict[str, Any]] | None
    ticket_validity_rules: list[dict[str, Any]] | None


class Booking(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: str | None
    connection_reference: Any | None
    created_at: str | None
    departure_time: str | None
    distribusion_booking_number: str | None
    duration: int | None
    flight_number: Any | None
    marketing_carrier_booking_number: str | None
    pax: int | None
    total_price: int | None
    fare_class: FareClass | None
    passengers: list[Passenger] | None
    segments: list[Segment] | None


class OrderCreateResponse(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    state: str
    created_at: str


class OrderResponse(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    state: str
    executed_at: str | None
    created_at: str | None
    booking: Booking | None
    currency: str | None


class TicketDocument(DistribusionBaseModel):
    ticket_content: bytes
    content_type: str | None
