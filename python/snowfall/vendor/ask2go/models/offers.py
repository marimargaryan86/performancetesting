from datetime import datetime, timedelta
from uuid import UUID

from pydantic import v1 as pydantic

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
    unit: str | None
    pieces: int
    has_free_baggage: bool
    passenger_type: str
    segment_index: int | None


class SegmentAircraft(CamelCaseBaseModel):
    flight_number: str
    equipment: str


class SegmentAvailability(CamelCaseBaseModel):
    booking_code: str
    count: int


class TripSegmentCarrier(CamelCaseBaseModel):
    code: str


class SegmentAmenity(CamelCaseBaseModel):
    exists: bool
    free: bool
    information: str | None


class SegmentAmenities(CamelCaseBaseModel):
    beverage: SegmentAmenity | None
    entertainment: SegmentAmenity | None
    food: SegmentAmenity | None
    power: SegmentAmenity | None
    wifi: SegmentAmenity | None


class TripSegment(CamelCaseBaseModel):
    id: UUID | None  # noqa: A003
    duration: timedelta
    distance: float
    cabin: str | None
    aircraft: SegmentAircraft
    availability: SegmentAvailability | None
    origin: TripOriginDestination
    destination: TripOriginDestination
    departure: TripDepartureArrival
    arrival: TripDepartureArrival
    marketing_carrier: TripSegmentCarrier
    operating_carrier: TripSegmentCarrier
    origin_terminal: str | None
    destination_terminal: str | None
    on_time_performance: float
    meal: str | None
    layover: str
    change_of_plane: bool | None
    segment_index: int | None
    segment_amenities: SegmentAmenities | None

    _normalize_duration = pydantic.validator("duration", pre=True, allow_reuse=True)(
        normalizers.normalize_duration,
    )


class Trip(CamelCaseBaseModel):
    id: UUID | None  # noqa: A003
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
    baggage_allowance: list[TripBaggageAllowance] | None
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
    brand_name: str | None


class BrandedPriceInformationfeature(CamelCaseBaseModel):
    baggage: list[TripBaggageAllowance] | None


class BrandedPriceInformation(CamelCaseBaseModel):
    base_fare: str
    total_tax: str
    total_cost: str
    original_cost: str
    service_fee: str
    currency: str
    brand_name: str | None
    brand_id: str | None
    fare_basis: list[str] | None
    is_refundable: bool = False
    features: list[BrandedPriceInformationfeature] | None


class PricingInformation(CamelCaseBaseModel):
    base: PricingInformationBase
    additional: list[BrandedPriceInformation] | None


class PassengerPricing(CamelCaseBaseModel):
    passenger_type: str
    quantity: int
    price_information: PricingInformationBase


class Offer(CamelCaseBaseModel):
    id: str | None  # noqa: A003
    is_refundable: bool
    docs_required: bool | None
    gds: str
    direction: str
    trips: list[Trip]
    pricing_information: PricingInformation
    passenger_pricing: list[PassengerPricing]
    search_id: str | None
