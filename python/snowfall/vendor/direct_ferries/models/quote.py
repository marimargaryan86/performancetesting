import datetime
from typing import Any, Optional, Sequence, Union

import pydantic

from snowfall.vendor.direct_ferries.models import base, leg


class Price(base.CamelCaseBaseModel):
    total_in_selected_currency: float


class QuoteBase(base.CamelCaseBaseModel):
    selected_currency: str
    partner_code: str
    is_different_outbound_return: bool
    return_alternative_routes: bool
    is_open_ticket: bool
    legs: Sequence[leg.LegBase]
    culture: str


class Quote(QuoteBase):
    quote_token: Optional[str]
    created_date_time: Optional[Union[datetime.datetime, str]]
    is_success: Optional[bool]
    price: Price
    is_special_offer: Optional[bool]
    has_ticket_types: Optional[bool]
    has_accommodations: Optional[bool]
    legs: Sequence[leg.Leg]
    pet_instructions: Optional[str]
    ticket_conditions: Optional[str]
    quote_messages: Optional[str]
    accommodation_message: Optional[str]
    required_passenger_information: Optional[Sequence[Any]]


class AccommodationResponse(base.CamelCaseBaseModel):
    culture: str
    currency: str
    partner_code: str
    legs: Sequence[leg.Leg]
    is_different_outbound_return: bool


class GenerateQuoteResponse(base.CamelCaseBaseModel):
    quote_token: str
    created_date_time: Optional[datetime.datetime]
    selected_currency: str
    partner_code: str
    is_different_outbound_return: bool
    return_alternative_routes: bool
    is_success: bool
    price: Price
    is_special_offer: bool
    is_open_ticket: bool
    has_ticket_types: bool
    has_accommodations: bool
    legs: Sequence[leg.Leg]
    pet_instructions: str
    ticket_conditions: str
    quote_messages: str
    culture: str


class Customer(base.CamelCaseBaseModel):
    identifier: Optional[int] = pydantic.Field(..., alias="id")
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    telephone: Optional[str]
    dial_code: Optional[str]
    is_mobile_number_valid: Optional[bool]


class Booking(base.CamelCaseBaseModel):
    identifier: Optional[int] = pydantic.Field(..., alias="id")
    booking_reference: Optional[str]
    is_cancelled: Optional[bool]
    is_amended: Optional[bool]
    is_confirmed: Optional[bool]
    created_date_time: Optional[datetime.datetime]
    selected_currency: Optional[str]
    partner_code: str
    is_different_outbound_return: Optional[bool]
    return_alternative_routes: Optional[bool]
    is_success: Optional[bool]
    no_quote_reason: Optional[str]
    price: Price
    is_special_offer: Optional[bool]
    is_open_ticket: Optional[bool]
    has_ticket_types: Optional[bool]
    has_accommodations: Optional[bool]
    customer: Optional[Customer]
    legs: Sequence[leg.Leg]
    pet_instructions: Optional[str]
    ticket_conditions: Optional[str]
    quote_messages: Optional[str]
    accommodation_message: Optional[str]
    required_passenger_information: Optional[Sequence[str]]
    culture: Optional[str]
