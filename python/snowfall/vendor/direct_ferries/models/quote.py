import datetime
from typing import Any, Optional, Sequence, Union

from snowfall.vendor.direct_ferries.models import base, common, leg


class QuoteBase(base.CamelCaseBaseModel):
    selected_currency: str
    partner_code: Optional[str]
    is_different_outbound_return: bool
    return_alternative_routes: bool
    is_open_ticket: bool
    legs: Sequence[leg.LegBase]


class Quote(QuoteBase):
    quote_token: Optional[str]
    created_date_time: Optional[Union[datetime.datetime, str]]
    is_success: Optional[bool]
    price: common.Price
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
    price: common.Price
    is_special_offer: bool
    is_open_ticket: bool
    has_ticket_types: bool
    has_accommodations: bool
    legs: Sequence[leg.Leg]
    pet_instructions: str
    ticket_conditions: str
    quote_messages: str
    culture: str
