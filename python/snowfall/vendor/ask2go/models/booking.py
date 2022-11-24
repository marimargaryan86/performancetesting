from typing import Any, Optional

from snowfall.vendor.ask2go.models import offers
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class InformationError(CamelCaseBaseModel):
    code: int
    message: Optional[str]


class Information(CamelCaseBaseModel):
    record_locators: Optional[list[str]]
    check_in_locators: Optional[list[str]]
    booking_id: int
    display_booking_id: Optional[str]
    status: str
    errors: Optional[list[InformationError]]
    warnings: Optional[str]


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
    id: str  # noqa: A003
    information: Information
    air_itinerary: offers.Offer
    price_information: dict[str, Any]
    travelers: list[dict[str, Any]]
    fare_rules: list[FareRules]
    contact_details: Optional[ContactDetails]
    transaction_id: str
    pricing_id: str
    search_id: str
