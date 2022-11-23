from typing import List, Optional

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class MarketingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str
    trade_name: str


class PassengerType(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    max_age: Optional[int] = None
    min_age: Optional[int] = None
    name: Optional[str] = None


class FareFeature(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None


class VehicleType(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None


class TicketValidityRule(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    rule_type: Optional[str] = None
    reference_time_type: Optional[str] = None
    use_type: Optional[str] = None
    offset_type: Optional[str] = None
    duration_type: Optional[str] = None
    offset: Optional[int] = None
    duration: Optional[int] = None


class FareClass(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: Optional[str] = None
    iata_category: Optional[str] = None
    journey_type: Optional[str] = None
    name: Optional[str] = None
    fare_features: Optional[List[FareFeature]] = None
    ticket_validity_rules: Optional[List[TicketValidityRule]] = None


class MarketingCarrierDetails(DistribusionBaseModel):
    code: str
    trade_name: str
    legal_name: str
    address: str
    phone: str
    fax: str
    customer_service_phone: str
    customer_service_email: str
    email: str
    commercial_register: str
    commercial_register_number: str
    vat_no: str
    authorised_representative: str
    white_label_logo: str
    white_label_colour_code: str
    terms: str
    privacy_policy: Optional[str]
    flight_number_required: bool
    has_mobile_tickets: bool
    tickets_validity_in_hours: Optional[str]
    tickets_validity_info: str
    cancellation_type: str
    status: str
    supports_seats: bool
    ticket_printing_required: bool
    booking_fee: int
    cancellation_fee: int
    cancellation_cutoff: Optional[int] = None
    default_passenger_type: Optional[PassengerType] = None
    fare_classes: Optional[List[FareClass]] = None
    passenger_types: Optional[List[PassengerType]] = None
    vehicle_types: Optional[List[VehicleType]] = None


class BookingSchema(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    mandatory: Optional[List[str]] = None
    optional: Optional[List[str]] = None
