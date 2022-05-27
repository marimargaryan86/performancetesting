from datetime import date, datetime
from typing import Optional, Sequence

from pydantic import BaseModel

from snowfall.vendor.save_a_train.enums import TripType
from snowfall.vendor.save_a_train.models.booking import Passenger


class GeneralSearchResultsRequest(BaseModel):
    origin_id: str
    destination_id: str
    trip_type: TripType
    number_of_passengers: int
    departure_date: date
    return_date: Optional[date] = None


class CreateSearchRequest(BaseModel):
    origin_id: str
    destination_id: str
    departure_datetime: datetime
    passengers_ages: list[int]


class SearchResultRequest(BaseModel):
    search_id: str
    search_result_id: int


class SelectSearchResultRequest(BaseModel):
    search_id: str
    search_result_id: int
    transfer_id: int
    fare_id: int


class CreateBookingRequest(BaseModel):
    search_id: str
    passengers: Sequence[Passenger]
    seat_preference_code: str = ""
