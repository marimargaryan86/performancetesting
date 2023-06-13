import datetime
from collections.abc import Sequence
from typing import Any

from snowfall.vendor.direct_ferries.models import base, common, leg


class QuoteBase(base.CamelCaseBaseModel):
    selected_currency: str
    partner_code: str | None
    is_different_outbound_return: bool
    return_alternative_routes: bool
    is_open_ticket: bool
    legs: Sequence[leg.LegBase]


class Quote(QuoteBase):
    quote_token: str | None
    created_date_time: datetime.datetime | str | None
    is_success: bool | None
    price: common.Price
    is_special_offer: bool | None
    has_ticket_types: bool | None
    has_accommodations: bool | None
    legs: Sequence[leg.Leg]
    pet_instructions: str | None
    ticket_conditions: str | None
    quote_messages: str | None
    accommodation_message: str | None
    required_passenger_information: Sequence[Any] | None


class AccommodationResponse(base.CamelCaseBaseModel):
    culture: str
    currency: str
    partner_code: str
    legs: Sequence[leg.Leg]
    is_different_outbound_return: bool


class GenerateQuoteResponse(base.CamelCaseBaseModel):
    quote_token: str
    created_date_time: datetime.datetime | None
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
