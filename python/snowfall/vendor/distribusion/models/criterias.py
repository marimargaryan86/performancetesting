import datetime

import pydantic

from snowfall.vendor.distribusion import enums
from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class FindConnectionsCriteria(DistribusionBaseModel):
    locale: str
    departure_stations: list[str]
    arrival_stations: list[str]
    departure_date: datetime.date
    pax: int
    currency: str


class ConnectionVacancyCriteria(DistribusionBaseModel):
    marketing_carrier: str
    departure_station: str
    arrival_station: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    return_departure_time: datetime.datetime | None
    return_arrival_time: datetime.datetime | None
    pax: list[int]
    passenger_type: list[str]
    fare_class: str | None
    currency: str


class ConnectionSeats(DistribusionBaseModel):
    marketing_carrier: str
    departure_station: str
    arrival_station: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime


class Passenger(DistribusionBaseModel):
    first_name: str
    last_name: str
    passenger_type: str = pydantic.Field(alias="type")


class ConnectedStationsCriteria(DistribusionBaseModel):
    page_size: int | None
    next_page: str | None
    carrier_code: str | None


class CreateOrder(DistribusionBaseModel):
    marketing_carrier: str
    departure_station: str
    arrival_station: str
    departure_time: str
    arrival_time: str
    title: str
    first_name: str
    last_name: str
    email: str
    phone: str
    city: str
    zip_code: str
    street_and_number: str
    execute_payment: bool
    payment_method: enums.PaymentMethod
    total_price: int
    pax: int
    terms_accepted: bool
    locale: str
    currency: str
    send_customer_email: bool
    fare_class: str
    passengers: list[Passenger]
