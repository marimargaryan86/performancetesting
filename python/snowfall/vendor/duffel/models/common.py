import datetime
from typing import List

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel


class Airline(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    name: str
    iata_code: str | None


class Aircraft(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    iata_code: str
    name: str


class City(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    name: str
    iata_code: str
    iata_country_code: str


class Airport(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    name: str
    iata_code: str | None
    icao_code: str | None
    iata_country_code: str
    latitude: float
    longitude: float
    time_zone: str
    city: City | None


class Place(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    name: str
    place_type: str = pydantic.Field(alias="type")
    iata_city_code: str | None
    iata_country_code: str
    latitude: float | None
    longitude: float | None
    icao_code: str | None
    time_zone: str | None
    city_name: str | None
    city: City | None
    airports: List[Airport] | None


class Refund(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    live_mode: bool
    payment_intent_id: str
    amount: str
    currency: str
    net_amount: str | None
    net_currency: str | None
    status: str
    destination: str
    arrival: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class LoyaltyProgrammeAccount(DuffelBaseModel):
    airline_iata_code: str
    account_number: str
