import datetime

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel


class Airline(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    name: str
    iata_code: str | None = None


class Aircraft(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    iata_code: str
    name: str


class City(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    name: str
    iata_code: str
    iata_country_code: str


class Airport(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    name: str
    iata_code: str | None = None
    icao_code: str | None = None
    iata_country_code: str
    latitude: float
    longitude: float
    time_zone: str
    city: City | None = None


class Place(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    name: str
    place_type: str = pydantic.Field(alias="type")
    iata_city_code: str | None = None
    iata_country_code: str
    latitude: float | None = None
    longitude: float | None = None
    icao_code: str | None = None
    time_zone: str | None = None
    city_name: str | None = None
    city: City | None = None
    airports: list[Airport] | None = None


class Refund(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    live_mode: bool
    payment_intent_id: str
    amount: str
    currency: str
    net_amount: str | None = None
    net_currency: str | None = None
    status: str
    destination: str
    arrival: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class LoyaltyProgrammeAccount(DuffelBaseModel):
    airline_iata_code: str
    account_number: str
