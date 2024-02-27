import datetime

import pydantic

from snowfall.vendor.ask2go.enums import DocumentType, Gender, PassengerType
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class AirportChildren(CamelCaseBaseModel):
    iata: str
    airport_name: str | None
    city: str | None
    country: str | None


class Airport(CamelCaseBaseModel):
    airport_name: str | None
    city: str | None
    country: str | None
    iata: str
    city_code: str | None
    is_parent: bool = False
    is_child: bool = False
    language: str | None
    fts_code: str | None
    fts_composite: str | None
    fts_full: str | None
    popularity: int = 0
    airport_children: list[AirportChildren] = pydantic.Field(default_factory=list)


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


class TravelerDocument(CamelCaseBaseModel):
    document_type: DocumentType
    document_number: str
    document_issue_country: str
    document_exp_date: datetime.date
    nationality: str


class Passenger(CamelCaseBaseModel):
    first_name: str
    last_name: str
    name_title: str
    gender: Gender
    type: PassengerType
    birth_date: datetime.date
    traveler_document: TravelerDocument | None
