import datetime
from typing import Optional

from snowfall.vendor.ask2go.enums import Gender, PassengerType
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class AirportChildren(CamelCaseBaseModel):
    iata: str
    airport_name: Optional[str]
    city: Optional[str]
    country: Optional[str]


class Airport(CamelCaseBaseModel):
    airport_name: Optional[str]
    city: Optional[str]
    country: Optional[str]
    iata: str
    city_code: Optional[str]
    is_parent: bool = False
    is_child: bool = False
    language: Optional[str]
    fts_code: Optional[str]
    fts_composite: Optional[str]
    fts_full: Optional[str]
    popularity: int = 0
    airport_children: list[AirportChildren] = []


class Phone(CamelCaseBaseModel):
    country_code: str
    number: str


class Country(CamelCaseBaseModel):
    code: str
    name: str


class Contact(CamelCaseBaseModel):
    address: str
    city: str
    postal_code: str
    country: Country  # location_models.Country
    phone: Phone  # Phone
    email: str


class Passenger(CamelCaseBaseModel):
    first_name: str
    last_name: str
    name_title: str
    gender: Gender
    type: PassengerType  # noqa: A003
    birth_date: datetime.date
