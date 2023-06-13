import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class MarketingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str
    trade_name: str


class PassengerType(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    description: str | None
    max_age: int | None
    min_age: int | None
    name: str | None


class FareFeature(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    description: str | None
    name: str | None


class VehicleType(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    description: str | None
    name: str | None


class TicketValidityRule(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    rule_type: str | None
    reference_time_type: str | None
    use_type: str | None
    offset_type: str | None
    duration_type: str | None
    offset: int | None
    duration: int | None


class FareClass(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str | None
    iata_category: str | None
    journey_type: str | None
    name: str | None
    fare_features: list[FareFeature] | None
    ticket_validity_rules: list[TicketValidityRule] | None


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
    privacy_policy: str | None
    flight_number_required: bool
    has_mobile_tickets: bool
    tickets_validity_in_hours: str | None
    tickets_validity_info: str
    cancellation_type: str
    status: str
    supports_seats: bool
    ticket_printing_required: bool
    booking_fee: int
    cancellation_fee: int
    cancellation_cutoff: int | None
    default_passenger_type: PassengerType | None
    fare_classes: list[FareClass] | None
    passenger_types: list[PassengerType] | None
    vehicle_types: list[VehicleType] | None


class BookingSchema(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    mandatory: list[str] | None
    optional: list[str] | None
