import datetime

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel
from snowfall.vendor.duffel.models.common import Aircraft, Airline, Airport, Place


class OrderSliceSegmentPassengerSeat(DuffelBaseModel):
    designator: str
    name: str
    disclosures: list[str]


class OrderSliceSegmentPassengerBaggage(DuffelBaseModel):
    baggage_type: str = pydantic.Field(alias="type")
    quantity: int


class OrderSliceSegmentPassenger(DuffelBaseModel):
    baggages: list[OrderSliceSegmentPassengerBaggage]
    cabin_class: str
    cabin_class_marketing_name: str
    passenger_id: str
    seat: OrderSliceSegmentPassengerSeat | None = None


class OrderSliceSegment(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
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
    passengers: list[OrderSliceSegmentPassenger]


class OrderSliceConditionChangeBeforeDeparture(DuffelBaseModel):
    allowed: bool
    penalty_amount: str | None = None
    penalty_currency: str | None = None


class OrderSliceConditions(DuffelBaseModel):
    change_before_departure: OrderSliceConditionChangeBeforeDeparture | None = None


class OrderSlice(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    changeable: bool | None = None
    destination_type: str
    destination: Place
    origin_type: str
    origin: Place
    duration: datetime.timedelta | None = None
    segments: list[OrderSliceSegment]
    conditions: OrderSliceConditions
