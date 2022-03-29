import datetime
from typing import Any

from snowfall.vendor.ask2go.enums import Gender, PassengerType
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


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
    name_title: Any  # enums.NameTitle
    gender: Gender
    type: PassengerType  # noqa: A003
    birth_date: datetime.date
