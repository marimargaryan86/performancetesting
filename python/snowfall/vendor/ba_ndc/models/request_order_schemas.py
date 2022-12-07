"""Contains order request schemas."""
import datetime
import uuid

import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.payer_details import Contact
from snowfall.vendor.ba_ndc.models.payment_type_schemas import (
    CashPayment,
    CreditCardPayment,
    VoucherPayment,
)
from snowfall.vendor.ba_ndc.models.util import passenger_enums


class Passenger(BaseSchema):
    """Passenger schema."""

    identifier: str = pydantic.Field(..., alias="id")
    passenger_type: passenger_enums.PassengerTypeEnum = pydantic.Field(
        ...,
        alias="type",
    )
    first_name: str = pydantic.Field(description="First name")
    last_name: str = pydantic.Field(description="Last name")
    name_title: str = pydantic.Field(description="Name title")
    birth_date: datetime.date = pydantic.Field(description="Birth date")
    gender: passenger_enums.GenderEnum = pydantic.Field(description="Gender")
    contact: Contact | None = pydantic.Field(description="Contact information")


class PassengerExtended(Passenger):
    """Passenger extended schema."""

    service_ids: list[uuid.UUID] = pydantic.Field(default_factory=list)


class PassengerPartial(BaseSchema):
    """Passenger partial schema."""

    identifier: str = pydantic.Field(..., alias="id")
    first_name: str = pydantic.Field("", description="First name")
    last_name: str = pydantic.Field("", description="Last name")
    name_title: str = pydantic.Field("", description="Name title")
    service_ids: list[uuid.UUID] = pydantic.Field(
        default_factory=list,
        description="Identifiers of services this passenger has",
    )

    # TODO: Extend


class CreateOrderRequest(BaseSchema):
    """Create order request schema."""

    offer_id: uuid.UUID = pydantic.Field(description="Offer identifier")
    passengers: list[PassengerExtended]
    payment: CreditCardPayment | CashPayment | VoucherPayment | None = pydantic.Field(
        description="Order payment",
        discriminator="payment_type",
    )


class UpdateOrderRequest(BaseSchema):
    """Update order request schema."""

    passengers: list[PassengerPartial] | None = pydantic.Field(
        description="Order passengers.",
        min_items=1,
    )
    payment: CreditCardPayment | CashPayment | VoucherPayment | None = pydantic.Field(
        description="Order payment",
        discriminator="payment_type",
    )
