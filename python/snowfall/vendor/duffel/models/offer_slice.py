import datetime
from typing import List

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel
from snowfall.vendor.duffel.models.common import Aircraft, Airline, Airport, Place


class OfferSliceConditionsChangeBeforeDeparture(DuffelBaseModel):
    allowed: bool
    penalty_amount: str | None
    penalty_currency: str | None


class OfferSliceConditions(DuffelBaseModel):
    change_before_departure: OfferSliceConditionsChangeBeforeDeparture | None


class OfferSliceSegmentPassengerBaggage(DuffelBaseModel):
    offer_type: str = pydantic.Field(alias="type")
    quantity: int


class OfferSliceSegmentPassenger(DuffelBaseModel):
    baggages: List[OfferSliceSegmentPassengerBaggage]
    cabin_class: str
    cabin_class_marketing_name: str
    passenger_id: str
    fare_basis_code: str | None


class OfferSliceSegment(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    aircraft: Aircraft | None
    arriving_at: datetime.datetime
    departing_at: datetime.datetime
    destination: Airport
    destination_terminal: str | None
    origin: Airport
    origin_terminal: str | None
    distance: str | None
    duration: str | None
    marketing_carrier: Airline
    marketing_carrier_flight_number: str
    operating_carrier: Airline
    operating_carrier_flight_number: str | None
    passengers: List[OfferSliceSegmentPassenger]


class OfferSlice(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    destination: Place
    destination_terminal: str | None
    origin: Place
    origin_terminal: str | None
    duration: str | None
    fare_brand_name: str | None
    segments: List[OfferSliceSegment]
    conditions: OfferSliceConditions
