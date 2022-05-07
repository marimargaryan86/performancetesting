from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from pydantic import AnyUrl, BaseModel

from snowfall.vendor.sat import enums
from snowfall.vendor.sat import normalizers as sat_normalizers
from snowfall.vendor.sat.models.search import StationName


class Passenger(BaseModel):
    title: enums.PassengerTitle
    first_name: str
    last_name: str
    date_of_birth: date
    gender: enums.PassengerGender
    email: str
    phone_number: str  # with country code, e.g. +442080160509
    country: str  # full country name, e.g. France


class TripInfo(BaseModel):
    origin_station_info: list[StationName]
    destination_station_info: list[StationName]
    departure: datetime
    arrival: datetime
    trip_duration: timedelta
    fare: str

    _normalize_time = sat_normalizers.normalizer(
        ("trip_duration",),
        sat_normalizers.normalize_time,
    )


class BookingResult(BaseModel):
    search_identifier: str
    outbound_trip_info: TripInfo
    inbound_trip_info: Optional[TripInfo]
    price: Decimal
    outbound_seat_reservation_fee: Decimal
    inbound_seat_reservation_fee: Optional[Decimal]
    total_price: Decimal


class BookingConfirmationResult(BaseModel):
    search_identifier: str
    issuing_info: str


class TicketInfo(BaseModel):
    url: AnyUrl
    confirmation_code: str
    status: str
