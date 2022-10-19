import datetime
from typing import Optional

import pydantic

from snowfall.vendor.ask2go import enums
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class PassengerCriteria(CamelCaseBaseModel):
    code: enums.PassengerType
    count: int


class AncillaryCriteria(CamelCaseBaseModel):
    code: str
    number_of_items: int


class SegmentCriteria(CamelCaseBaseModel):
    trip_number: int
    segment_number: int
    flight_number: str
    departure_date: datetime.datetime
    arrival_date: datetime.datetime
    origin_iata: str
    destination_iata: str
    marketing_airline: str
    operating_airline: str
    equipment: str
    res_book_desig_code: Optional[str]


class ValidateOfferCriteria(CamelCaseBaseModel):
    transaction_id: str
    client_ip: Optional[str]
    currency: str
    flight_segments: list[SegmentCriteria]
    passengers: list[PassengerCriteria]
    ancillaries: Optional[list[AncillaryCriteria]]


class ValidateOfferResponse(CamelCaseBaseModel):
    identifier: str = pydantic.Field(alias="id")
    transaction_id: str
