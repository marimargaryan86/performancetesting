from typing import Any, Dict, List

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class CancellationsId(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")


class City(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    name: str | None


class FareFeature(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    description: str | None
    name: str | None


class MarketingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    address: str | None
    authorised_representative: str | None
    booking_fee: int | None
    cancellation_cutoff: int | None
    cancellation_fee: int | None
    cancellation_type: str | None
    code: str | None
    commercial_register: str | None
    commercial_register_number: str | None
    customer_service_email: str | None
    customer_service_phone: str | None
    email: str | None
    fax: str | None
    flight_number_required: bool | None
    legal_name: str | None
    phone: str | None
    terms: str | None
    trade_name: str | None
    vat_no: str | None
    white_label_colour_code: str | None
    white_label_logo: str | None


class OperatingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    legal_name: str | None
    trade_name: str | None


class Passenger(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    first_name: str | None
    last_name: str | None
    serial_code: Any | None


class SegmentPassenger(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    seat_number: Any | None
    passenger: Passenger | None


class Station(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    description: str | None
    latitude: float | None
    longitude: float | None
    name: str | None
    station_type: str | None
    street_and_number: str | None
    time_zone: str | None
    zip_code: str | None
    area: Any | None
    city: City | None


class VehicleType(DistribusionBaseModel):
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
    passenger_group_rules: List[Dict[str, Any]] | None
    ticket_validity_rules: List[Dict[str, Any]] | None


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
    segment_passengers: List[SegmentPassenger] | None
    vehicle: Vehicle | None


class Connection(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: str | None
    departure_time: str | None
    arrival_station: Station | None
    departure_station: Station | None
    fees: Dict[str, Any] | None
    marketing_carrier: MarketingCarrier | None
    segments: List[Segment] | None


class Booking(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    arrival_time: str | None
    city: str | None
    connection_reference: Any | None
    created_at: str | None
    departure_time: str | None
    distribusion_booking_number: str | None
    duration: int | None
    email: str | None
    execute_payment: bool | None
    first_name: str | None
    flight_number: Any | None
    last_name: str | None
    marketing_carrier_booking_number: Any | None
    pax: int | None
    payer_id: Any | None
    payment_method: str | None
    payment_token: Any | None
    phone: str | None
    retailer_partner_number: str | None
    send_customer_email: bool | None
    send_marketing_emails: Any | None
    street_and_number: str | None
    terms_accepted: bool | None
    title: str | None
    total_price: int | None
    currency: str
    zip_code: str | None
    arrival_station: Station | None
    cancellation: CancellationsId | None
    custom_fields: Dict[str, Any] | None
    departure_station: Station | None
    extras: Dict[str, Any] | None
    fare_class: FareClass | None
    fees: Dict[str, Any] | None
    inbound_connection: Any | None
    installments: Any | None
    marketing_carrier: MarketingCarrier | None
    outbound_connection: Connection | None
    passengers: List[Passenger] | None
    segments: List[Segment] | None
