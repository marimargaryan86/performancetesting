import datetime

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel
from snowfall.vendor.duffel.models.common import Aircraft, Airline, Airport, Place


class OfferSliceConditionsChangeBeforeDeparture(DuffelBaseModel):
    allowed: bool
    penalty_amount: str | None = None
    penalty_currency: str | None = None


class OfferSliceConditions(DuffelBaseModel):
    change_before_departure: OfferSliceConditionsChangeBeforeDeparture | None


class OfferSliceSegmentPassengerBaggage(DuffelBaseModel):
    baggage_type: str = pydantic.Field(alias="type")
    quantity: int


class OfferSliceSegmentPassenger(DuffelBaseModel):
    baggages: list[OfferSliceSegmentPassengerBaggage]
    cabin_class: str
    cabin_class_marketing_name: str
    passenger_id: str
    fare_basis_code: str | None = None


class Stop(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    duration: datetime.timedelta | None
    departing_at: datetime.datetime
    arriving_at: datetime.datetime
    airport: Airport


class OfferSliceSegment(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    stops: list[Stop] | None = None
    aircraft: Aircraft | None = None
    arriving_at: datetime.datetime
    departing_at: datetime.datetime
    destination: Airport
    destination_terminal: str | None = None
    origin: Airport
    origin_terminal: str | None = None
    distance: str | None = None
    duration: datetime.timedelta | None = None
    marketing_carrier: Airline
    marketing_carrier_flight_number: str
    operating_carrier: Airline
    operating_carrier_flight_number: str | None = None
    passengers: list[OfferSliceSegmentPassenger]


class OfferSlice(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    destination: Place
    destination_terminal: str | None = None
    origin: Place
    origin_terminal: str | None = None
    duration: datetime.timedelta | None = None
    fare_brand_name: str | None = None
    segments: list[OfferSliceSegment]
    conditions: OfferSliceConditions
