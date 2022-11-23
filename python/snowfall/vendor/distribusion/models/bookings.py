from typing import Any, Dict, List, Optional

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class CancellationsId(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")


class City(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    name: Optional[str] = None


class FareFeature(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None


class MarketingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    address: Optional[str] = None
    authorised_representative: Optional[str] = None
    booking_fee: Optional[int] = None
    cancellation_cutoff: Optional[int] = None
    cancellation_fee: Optional[int] = None
    cancellation_type: Optional[str] = None
    code: Optional[str] = None
    commercial_register: Optional[str] = None
    commercial_register_number: Optional[str] = None
    customer_service_email: Optional[str] = None
    customer_service_phone: Optional[str] = None
    email: Optional[str] = None
    fax: Optional[str] = None
    flight_number_required: Optional[bool] = None
    legal_name: Optional[str] = None
    phone: Optional[str] = None
    terms: Optional[str] = None
    trade_name: Optional[str] = None
    vat_no: Optional[str] = None
    white_label_colour_code: Optional[str] = None
    white_label_logo: Optional[str] = None


class OperatingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None


class Passenger(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    serial_code: Optional[Any] = None


class SegmentPassenger(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    seat_number: Optional[Any] = None
    passenger: Optional[Passenger] = None


class Station(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    name: Optional[str] = None
    station_type: Optional[str] = None
    street_and_number: Optional[str] = None
    time_zone: Optional[str] = None
    zip_code: Optional[str] = None
    area: Optional[Any] = None
    city: Optional[City] = None


class VehicleType(DistribusionBaseModel):
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
    passenger_group_rules: Optional[List[Dict[str, Any]]] = None  # noqa: WPS234
    ticket_validity_rules: Optional[List[Dict[str, Any]]] = None  # noqa: WPS234


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
    segment_passengers: Optional[List[SegmentPassenger]] = None
    vehicle: Optional[Vehicle] = None


class Connection(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_station: Optional[Station] = None
    departure_station: Optional[Station] = None
    fees: Optional[Dict[str, Any]] = None
    marketing_carrier: Optional[MarketingCarrier] = None
    segments: Optional[List[Segment]] = None


class Booking(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: Optional[str] = None
    city: Optional[str] = None
    connection_reference: Optional[Any] = None
    created_at: Optional[str] = None
    departure_time: Optional[str] = None
    distribusion_booking_number: Optional[str] = None
    duration: Optional[int] = None
    email: Optional[str] = None
    execute_payment: Optional[bool] = None
    first_name: Optional[str] = None
    flight_number: Optional[Any] = None
    last_name: Optional[str] = None
    marketing_carrier_booking_number: Optional[Any] = None
    pax: Optional[int] = None
    payer_id: Optional[Any] = None
    payment_method: Optional[str] = None
    payment_token: Optional[Any] = None
    phone: Optional[str] = None
    retailer_partner_number: Optional[str] = None
    send_customer_email: Optional[bool] = None
    send_marketing_emails: Optional[Any] = None
    street_and_number: Optional[str] = None
    terms_accepted: Optional[bool] = None
    title: Optional[str] = None
    total_price: Optional[int] = None
    zip_code: Optional[str] = None
    arrival_station: Optional[Station] = None
    cancellation: Optional[CancellationsId] = None
    custom_fields: Optional[Dict[str, Any]] = None
    departure_station: Optional[Station] = None
    extras: Optional[Dict[str, Any]] = None
    fare_class: Optional[FareClass] = None
    fees: Optional[Dict[str, Any]] = None
    inbound_connection: Optional[Any] = None
    installments: Optional[Any] = None
    marketing_carrier: Optional[MarketingCarrier] = None
    outbound_connection: Optional[Connection] = None
    passengers: Optional[List[Passenger]] = None
    segments: Optional[List[Segment]] = None
