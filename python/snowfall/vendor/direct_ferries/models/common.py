import datetime
from collections.abc import Sequence

import pydantic

from snowfall.vendor.direct_ferries import normalizers
from snowfall.vendor.direct_ferries.models import base, leg


class Price(base.CamelCaseBaseModel):
    total_in_selected_currency: float


class Customer(base.CamelCaseBaseModel):
    identifier: int | None = pydantic.Field(..., alias="id")
    first_name: str | None
    last_name: str | None
    email: str | None
    telephone: str | None
    dial_code: str | None
    is_mobile_number_valid: bool | None


class Booking(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    booking_reference: str
    booking_token: str
    is_cancelled: bool | None
    is_amended: bool | None
    is_confirmed: bool | None
    created_date_time: datetime.datetime
    selected_currency: str | None
    partner_code: str
    is_different_outbound_return: bool | None
    return_alternative_routes: bool | None
    is_success: bool | None
    no_quote_reason: str | None
    price: Price
    is_special_offer: bool | None
    is_open_ticket: bool | None
    has_ticket_types: bool | None
    has_accommodations: bool | None
    customer: Customer | None
    legs: Sequence[leg.Leg]
    pet_instructions: str | None
    ticket_conditions: str | None
    quote_messages: str | None
    accommodation_message: str | None
    required_passenger_information: Sequence[str] | None
    culture: str | None

    _normalize_booking_token = pydantic.validator(
        "booking_token",
        pre=True,
        allow_reuse=True,
    )(
        normalizers.normalize_booking_token,
    )
