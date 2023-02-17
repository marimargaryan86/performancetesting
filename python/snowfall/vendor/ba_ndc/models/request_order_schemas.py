"""Contains order request schemas."""
import datetime
import uuid

import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.payer_details import (
    Contact,
    DestinationResidenceDetails,
)
from snowfall.vendor.ba_ndc.models.payment_type_schemas import (
    CashPayment,
    CreditCardPayment,
    VoucherPayment,
)
from snowfall.vendor.ba_ndc.models.util import passenger_enums


class IdentityDocument(BaseSchema):
    document_number: str = pydantic.Field(description="Document number")
    document_type: str = pydantic.Field(description="Document type")
    birth_date: datetime.date = pydantic.Field(description="Birth date")
    nationality: str = pydantic.Field(description="Passenger nationality")
    issuing_country: str = pydantic.Field(description="Document issuing country")
    expiration_date: datetime.date = pydantic.Field(
        description="Document expiration date",
    )


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
    identity_documents: list[IdentityDocument] = pydantic.Field(default_factory=list)


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
    identity_documents: list[IdentityDocument] = pydantic.Field(
        default_factory=list,
        description="Identity documents list associated to this passenger",
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
    destination_residence_details: DestinationResidenceDetails | None = pydantic.Field(
        description="Residence details for passengers traveling to USA",
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
