from datetime import datetime, time
from decimal import Decimal
from typing import Optional
from uuid import UUID

from snowfall.providers.ask2go.enums import AirCabinClassType
from snowfall.providers.ask2go.models.base import CamelCaseBaseModel


class TripOriginDestination(CamelCaseBaseModel):
    airport_code: str


class TripDepartureArrival(CamelCaseBaseModel):
    date_time: datetime


class TripPlattingCarrier(CamelCaseBaseModel):
    code: str


class TripBaggageAllowance(CamelCaseBaseModel):
    weight: float
    unit: str
    pieces: int
    has_free_baggage: bool
    passenger_type: str


class SegmentAircraft(CamelCaseBaseModel):
    flight_number: str
    equipment: str


class SegmentAvailability(CamelCaseBaseModel):
    booking_code: str
    count: int


class TripSegmentCarrier(CamelCaseBaseModel):
    code: str


class TripSegment(CamelCaseBaseModel):
    id: UUID  # noqa: A003
    duration: time
    distance: float
    cabin: AirCabinClassType
    is_technical_stop: bool
    aircraft: SegmentAircraft
    availability: SegmentAvailability
    origin: TripOriginDestination
    destination: TripOriginDestination
    departure: TripDepartureArrival
    arrival: TripDepartureArrival
    marketing_carrier: TripSegmentCarrier
    operating_carrier: TripSegmentCarrier
    origin_terminal: Optional[str]
    destination_terminal: Optional[str]
    on_time_performance: float
    meal: Optional[str]
    layover: str
    change_of_plane: bool


class Trip(CamelCaseBaseModel):
    id: UUID  # noqa: A003
    duration: time
    direction: str
    is_red_eye: bool
    has_long_connection_duration: bool
    number_of_stops: int
    origin: TripOriginDestination
    destination: TripOriginDestination
    departure: TripDepartureArrival
    arrival: TripDepartureArrival
    platting_carrier: TripPlattingCarrier
    segments: list[TripSegment]
    baggage_allowance: list[TripBaggageAllowance]
    gds: str


class PricingInformationBase(CamelCaseBaseModel):
    base_fare: Decimal
    total_tax: Decimal
    total_cost: Decimal
    original_cost: Decimal
    service_fee: Decimal
    currency: str


class PricingInformation(CamelCaseBaseModel):
    base: PricingInformationBase


class PassengerPricing(CamelCaseBaseModel):
    passenger_type: str
    quantity: int
    price_information: PricingInformationBase


class Offer(CamelCaseBaseModel):
    id: UUID  # noqa: A003
    is_refundable: bool
    docs_required: bool
    gds: str
    direction: str
    trips: list[Trip]
    pricing_information: PricingInformation
    passenger_pricing: list[PassengerPricing]
