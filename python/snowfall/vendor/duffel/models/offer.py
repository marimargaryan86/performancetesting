import datetime
import enum

from pydantic import v1 as pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel
from snowfall.vendor.duffel.models.common import Airline, LoyaltyProgrammeAccount
from snowfall.vendor.duffel.models.offer_slice import OfferSlice


class OfferCondition(DuffelBaseModel):
    allowed: bool
    penalty_amount: str | None
    penalty_currency: str | None


class OfferConditions(DuffelBaseModel):
    change_before_departure: OfferCondition | None
    refund_before_departure: OfferCondition | None


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
    passenger_ids: list[str]
    segment_ids: list[str]
    total_amount: str
    total_currency: str
    service_type: str | None = pydantic.Field(..., alias="type")


class OfferPassenger(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    age: int | None
    passenger_type: str = pydantic.Field(alias="type")
    given_name: str | None
    family_name: str | None
    loyalty_programme_accounts: list[LoyaltyProgrammeAccount]


class PrivateFareType(enum.StrEnum):
    corporate = "corporate"
    leisure = "leisure"
    negotiated = "negotiated"


class PrivateFare(DuffelBaseModel):
    corporate_code: str | None
    tracking_reference: str | None
    tour_code: str | None
    fare_type: PrivateFareType | None = pydantic.Field(None, alias="type")


class Offer(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    live_mode: bool
    allowed_passenger_identity_document_types: list[str]
    available_services: list[Service] | None
    base_amount: str
    base_currency: str
    conditions: OfferConditions
    created_at: datetime.datetime
    updated_at: datetime.datetime
    expires_at: datetime.datetime
    owner: Airline
    passenger_identity_documents_required: bool
    passengers: list[OfferPassenger]
    payment_requirements: PaymentRequirements
    slices: list[OfferSlice]
    tax_amount: str | None
    tax_currency: str | None
    total_emissions_kg: str
    total_amount: str
    total_currency: str
    private_fares: list[PrivateFare] | None
