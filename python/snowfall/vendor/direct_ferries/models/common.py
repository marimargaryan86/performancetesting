import datetime
from typing import Optional, Sequence

import pydantic

from snowfall.vendor.direct_ferries import normalizers
from snowfall.vendor.direct_ferries.models import base, leg


class Price(base.CamelCaseBaseModel):
    total_in_selected_currency: float


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
    booking_token: Optional[str]
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

    _normalize_booking_token = pydantic.validator(
        "booking_token",
        pre=True,
        allow_reuse=True,
    )(
        normalizers.normalize_booking_token,
    )
