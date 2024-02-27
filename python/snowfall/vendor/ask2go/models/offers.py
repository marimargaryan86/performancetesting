from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

import pydantic

from snowfall.vendor.ask2go import normalizers
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel

Duration = Annotated[
    timedelta,
    pydantic.BeforeValidator(normalizers.normalize_duration),
]


class TripOriginDestinationFlight(CamelCaseBaseModel):
    airport_code: str


class TripOriginDestinationRail(CamelCaseBaseModel):
    trainstation_code: str
    trainstation_name: str


TripOriginDestination = TripOriginDestinationFlight | TripOriginDestinationRail


class TripDepartureArrival(CamelCaseBaseModel):
    date_time: datetime


class TripPlattingCarrier(CamelCaseBaseModel):
    code: str


class TripBaggageAllowance(CamelCaseBaseModel):
    weight: float
    unit: str | None = None
    pieces: int
    has_free_baggage: bool
    passenger_type: str
    segment_index: int | None = None


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
    information: str | None = None


class SegmentAmenities(CamelCaseBaseModel):
    beverage: SegmentAmenity | None = None
    entertainment: SegmentAmenity | None = None
    food: SegmentAmenity | None = None
    power: SegmentAmenity | None = None
    wifi: SegmentAmenity | None = None


class TripSegment(CamelCaseBaseModel):
    id: UUID | None = None
    duration: Duration
    distance: float
    cabin: str | None = None
    aircraft: SegmentAircraft
    availability: SegmentAvailability | None = None
    origin: TripOriginDestination = pydantic.Field(union_mode="left_to_right")
    destination: TripOriginDestination = pydantic.Field(union_mode="left_to_right")
    departure: TripDepartureArrival
    arrival: TripDepartureArrival
    marketing_carrier: TripSegmentCarrier
    operating_carrier: TripSegmentCarrier
    origin_terminal: str | None = None
    destination_terminal: str | None = None
    on_time_performance: float
    meal: str | None = None
    layover: str
    change_of_plane: bool | None = None
    segment_index: int | None = None
    segment_amenities: SegmentAmenities | None = None


class Trip(CamelCaseBaseModel):
    id: UUID | None = None
    duration: Duration
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
    baggage_allowance: list[TripBaggageAllowance] = pydantic.Field(default_factory=list)
    gds: str


class PricingInformationBase(CamelCaseBaseModel):
    base_fare: str
    total_tax: str
    total_cost: str
    original_cost: str
    service_fee: str
    currency: str
    brand_name: str | None = None


class BrandedPriceInformationFeature(CamelCaseBaseModel):
    baggage: list[TripBaggageAllowance] = pydantic.Field(default_factory=list)


class BrandedPriceInformation(PricingInformationBase):
    brand_id: str | None = None
    fare_basis: list[str] = pydantic.Field(default_factory=list)
    is_refundable: bool = False
    features: list[BrandedPriceInformationFeature] = pydantic.Field(
        default_factory=list,
    )


class PricingInformation(CamelCaseBaseModel):
    base: PricingInformationBase
    additional: list[BrandedPriceInformation] = pydantic.Field(default_factory=list)


class PassengerPricing(CamelCaseBaseModel):
    passenger_type: str
    quantity: int
    price_information: PricingInformationBase


class Offer(CamelCaseBaseModel):
    id: str | None = None
    is_refundable: bool = False
    docs_required: bool | None = None
    gds: str
    direction: str
    trips: list[Trip]
    pricing_information: PricingInformation
    passenger_pricing: list[PassengerPricing]
    search_id: str | None = None
