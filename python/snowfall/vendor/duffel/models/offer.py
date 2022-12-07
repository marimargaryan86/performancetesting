import datetime
from typing import List

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel
from snowfall.vendor.duffel.models.common import Airline, LoyaltyProgrammeAccount
from snowfall.vendor.duffel.models.offer_slice import OfferSlice


class OfferConditionChangeBeforeDeparture(DuffelBaseModel):
    allowed: bool
    penalty_amount: str | None
    penalty_currency: str | None


class OfferConditionRefundBeforeDeparture(DuffelBaseModel):
    allowed: bool
    penalty_amount: str | None
    penalty_currency: str | None


class OfferConditions(DuffelBaseModel):
    change_before_departure: OfferConditionChangeBeforeDeparture | None
    refund_before_departure: OfferConditionRefundBeforeDeparture | None


class PaymentRequirements(DuffelBaseModel):
    payment_required_by: datetime.datetime | None
    price_guarantee_expires_at: datetime.datetime | None
    requires_instant_payment: bool


class ServiceMetadata(DuffelBaseModel):
    metadata_type: str | None = pydantic.Field(alias="type")
    maximum_weight_kg: int | None
    maximum_height_cm: int | None
    maximum_length_cm: int | None
    maximum_depth_cm: int | None


class Service(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    maximum_quantity: int
    metadata: ServiceMetadata
    passenger_ids: List[str]
    segment_ids: List[str]
    total_amount: str
    total_currency: str
    service_type: str | None = pydantic.Field(..., alias="type")


class OfferPassenger(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    age: int | None
    passenger_type: str = pydantic.Field(alias="type")
    given_name: str | None
    family_name: str | None
    loyalty_programme_accounts: List[LoyaltyProgrammeAccount]


class Offer(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    live_mode: bool
    allowed_passenger_identity_document_types: List[str]
    available_services: List[Service] | None
    base_amount: str
    base_currency: str
    conditions: OfferConditions
    created_at: datetime.datetime
    updated_at: datetime.datetime
    expires_at: datetime.datetime
    owner: Airline
    passenger_identity_documents_required: bool
    passengers: List[OfferPassenger]
    payment_requirements: PaymentRequirements
    slices: List[OfferSlice]
    tax_amount: str | None
    tax_currency: str | None
    total_emissions_kg: str
    total_amount: str
    total_currency: str
