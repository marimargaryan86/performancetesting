from datetime import date, datetime, timedelta

from pydantic.v1 import BaseModel

from snowfall.vendor.save_a_train import enums
from snowfall.vendor.save_a_train import normalizers as save_a_train_normalizers
from snowfall.vendor.save_a_train.models.search import StationName


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

    _normalize_time = save_a_train_normalizers.normalizer(
        ("trip_duration",),
        save_a_train_normalizers.normalize_time,
    )


class BookingResult(BaseModel):
    search_identifier: str
    outbound_trip_info: TripInfo
    inbound_trip_info: TripInfo | None
    price: str
    outbound_seat_reservation_fee: str
    inbound_seat_reservation_fee: str | None
    total_price: str


class BookingConfirmationResult(BaseModel):
    search_identifier: str
    issuing_info: str


class TicketInfo(BaseModel):
    url: str
    confirmation_code: str
    status: str


class BookingInformation(BaseModel):
    identifier: str
    outbound_trip_info: TripInfo
    inbound_trip_info: TripInfo | None
    placed_on: str
    outbound_seat_reservation_fee: str
    inbound_seat_reservation_fee: str | None
    total_price: str
    order_status: str
    order_email: str
    order_phone: str
