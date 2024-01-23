from typing import Any

import pydantic

from snowfall.vendor.ask2go.models import offers
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class InformationError(CamelCaseBaseModel):
    code: int
    message: str | None


class Information(CamelCaseBaseModel):
    record_locators: list[str] = pydantic.Field(default_factory=list)
    check_in_locators: list[str] = pydantic.Field(default_factory=list)
    booking_id: int
    display_booking_id: str | None = None
    status: str
    errors: list[InformationError] = pydantic.Field(default_factory=list)
    warnings: list[str] = pydantic.Field(default_factory=list)


class ContactDetailsAddress(CamelCaseBaseModel):
    street: str
    city: str
    postal_code: str
    country_code: str


class FareRule(CamelCaseBaseModel):
    text: str
    title: str


class FareRules(CamelCaseBaseModel):
    origin: str
    destination: str
    fare_basis: str
    fare_rule: list[FareRule]


class ContactDetails(CamelCaseBaseModel):
    first_name: str
    last_name: str
    address: ContactDetailsAddress
    mobile_phone: str
    email: str


class Booking(CamelCaseBaseModel):
    id: str
    information: Information
    air_itinerary: offers.Offer
    price_information: dict[str, Any]
    travelers: list[dict[str, Any]]
    fare_rules: list[FareRules]
    contact_details: ContactDetails | None = None
    transaction_id: str
    pricing_id: str
    search_id: str
