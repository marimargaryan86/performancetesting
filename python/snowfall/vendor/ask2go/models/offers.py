from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import pydantic

from snowfall.vendor.ask2go import normalizers
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class TripOriginDestination(CamelCaseBaseModel):
    airport_code: str


class TripDepartureArrival(CamelCaseBaseModel):
    date_time: datetime


class TripPlattingCarrier(CamelCaseBaseModel):
    code: str


class TripBaggageAllowance(CamelCaseBaseModel):
    weight: float
    unit: Optional[str]
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
    id: Optional[UUID]  # noqa: A003
    duration: timedelta
    distance: float
    cabin: Optional[str]
    is_technical_stop: bool
    aircraft: SegmentAircraft
    availability: Optional[SegmentAvailability]
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
    change_of_plane: Optional[bool]

    _normalize_duration = pydantic.validator("duration", pre=True, allow_reuse=True)(
        normalizers.normalize_duration,
    )


class Trip(CamelCaseBaseModel):
    id: Optional[UUID]  # noqa: A003
    duration: timedelta
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

    _normalize_duration = pydantic.validator("duration", pre=True, allow_reuse=True)(
        normalizers.normalize_duration,
    )


class PricingInformationBase(CamelCaseBaseModel):
    base_fare: str
    total_tax: str
    total_cost: str
    original_cost: str
    service_fee: str
    currency: str


class PricingInformation(CamelCaseBaseModel):
    base: PricingInformationBase


class PassengerPricing(CamelCaseBaseModel):
    passenger_type: str
    quantity: int
    price_information: PricingInformationBase


class Offer(CamelCaseBaseModel):
    id: str  # noqa: A003
    is_refundable: bool
    docs_required: Optional[bool]
    gds: str
    direction: str
    trips: list[Trip]
    pricing_information: PricingInformation
    passenger_pricing: list[PassengerPricing]
