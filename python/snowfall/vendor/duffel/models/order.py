import datetime
from typing import Any

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel
from snowfall.vendor.duffel.models.common import Airline, LoyaltyProgrammeAccount
from snowfall.vendor.duffel.models.order_conditions import OrderConditions
from snowfall.vendor.duffel.models.order_slice import OrderSlice


class OrderServiceMetadataSeat(DuffelBaseModel):
    designator: str
    name: str
    disclosures: list[str]


class OrderServiceMetadataBaggage(DuffelBaseModel):
    baggage_type: str = pydantic.Field(..., alias="type")
    maximum_weight_kg: int | None
    maximum_height_cm: int | None
    maximum_length_cm: int | None
    maximum_depth_cm: int | None


class OrderService(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    metadata: OrderServiceMetadataSeat | OrderServiceMetadataBaggage
    passenger_ids: list[str]
    quantity: int
    segment_ids: list[str]
    total_amount: str
    total_currency: str
    service_type: str = pydantic.Field(..., alias="type")


class OrderPaymentStatus(DuffelBaseModel):
    awaiting_payment: bool
    payment_required_by: datetime.datetime | None
    price_guarantee_expires_at: datetime.datetime | None


class OrderPassenger(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    passenger_type: str = pydantic.Field(..., alias="type")
    infant_passenger_id: str | None
    given_name: str
    family_name: str
    gender: str
    title: str | None
    born_on: datetime.date | None
    loyalty_programme_accounts: list[LoyaltyProgrammeAccount]


class OrderDocument(DuffelBaseModel):
    document_type: str = pydantic.Field(..., alias="type")
    unique_identifier: str


class Order(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    live_mode: bool
    available_actions: list[str]
    base_amount: str | None
    base_currency: str | None
    booking_reference: str
    cancelled_at: datetime.datetime | None
    content: str  # noqa: WPS110
    created_at: datetime.datetime
    synced_at: datetime.datetime | None
    documents: list[OrderDocument]
    passengers: list[OrderPassenger]
    payment_status: OrderPaymentStatus
    services: list[OrderService]
    slices: list[OrderSlice]
    conditions: OrderConditions
    owner: Airline
    tax_amount: str
    tax_currency: str | None
    total_amount: str
    total_currency: str
    metadata: dict[str, Any] | None


class OrderResponse(DuffelBaseModel):
    response_data: Order = pydantic.Field(..., alias="data")
