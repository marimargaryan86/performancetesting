import datetime
from typing import Literal

import pydantic

from snowfall.vendor.benerail.enums import Gender
from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import Supplier


class ReductionCard(BenerailBaseModel):
    href: str | None
    card_value: str | None = pydantic.Field(..., alias="value")


class PassengerRequestCards(BenerailBaseModel):
    card_type: str = pydantic.Field(..., alias="type")
    number: str | None


class PassengerCards(BenerailBaseModel):
    card_type: ReductionCard | None = pydantic.Field(..., alias="type")
    number: str | None


class PassengerRequestCorporateContracts(BenerailBaseModel):
    contract_nr: str
    supplier: str
    fce: str | None


class PassengerCorporateContracts(BenerailBaseModel):
    contract_number: str | None
    supplier: Supplier | None
    fce: str | None


class PassengerDetail(BenerailBaseModel):
    preferred_language: str | None
    title: str | None
    first_name: str | None
    last_name: str | None
    email: str | None
    phone_number: str | None


class PassengerRequest(BenerailBaseModel):
    external_reference: str | None
    date_of_birth: datetime.date | None
    cards: list[PassengerRequestCards] | None
    corporate_contracts: list[PassengerRequestCorporateContracts] | None
    gender: Gender | None
    details: PassengerDetail | None


class Passenger(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    external_reference: str | None
    date_of_birth: datetime.date | None
    cards: list[PassengerCards] | None
    corporate_contracts: list[PassengerCorporateContracts] | None
    gender: Gender | None
    details: PassengerDetail | None
    passenger_status: Literal["created", "in use", "immutable"] | None
