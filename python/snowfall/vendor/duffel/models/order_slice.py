import datetime
from typing import List

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel
from snowfall.vendor.duffel.models.common import Aircraft, Airline, Airport, Place


class OrderSliceSegmentPassengerSeat(DuffelBaseModel):
    designator: str
    name: str
    disclosures: List[str]


class OrderSliceSegmentPassengerBaggage(DuffelBaseModel):
    baggage_type: str = pydantic.Field(..., alias="type")
    quantity: int


class OrderSliceSegmentPassenger(DuffelBaseModel):
    baggages: List[OrderSliceSegmentPassengerBaggage]
    cabin_class: str
    cabin_class_marketing_name: str
    passenger_id: str
    seat: OrderSliceSegmentPassengerSeat | None


class OrderSliceSegment(DuffelBaseModel):
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
    passengers: List[OrderSliceSegmentPassenger]


class OrderSliceConditionChangeBeforeDeparture(DuffelBaseModel):
    allowed: bool
    penalty_amount: str | None
    penalty_currency: str | None


class OrderSliceConditions(DuffelBaseModel):
    change_before_departure: OrderSliceConditionChangeBeforeDeparture | None


class OrderSlice(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    changeable: bool | None
    destination_type: str
    destination: Place
    origin_type: str
    origin: Place
    duration: str | None
    segments: List[OrderSliceSegment]
    conditions: OrderSliceConditions
