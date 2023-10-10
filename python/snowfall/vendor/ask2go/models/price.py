import datetime
from typing import Any

import pydantic

from snowfall.vendor.ask2go import enums
from snowfall.vendor.ask2go.models import booking, offers
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class OfferPriceDoc(CamelCaseBaseModel):
    doc_type: enums.OfferPriceDocType
    required_date_of_birth: bool
    required_nationality: bool
    required_expiration_date: bool
    required_issuing_country: bool
    required_passport_number: bool


class PriceCurrency(CamelCaseBaseModel):
    price: str
    currency: str


class PricingResponseInformation(CamelCaseBaseModel):
    old_price: PriceCurrency
    new_price: PriceCurrency


class PenaltyInformation(CamelCaseBaseModel):
    penalty_type: enums.PenaltyType
    changeable: bool | None = None
    refundable: bool
    applicability: enums.Applicability
    amount: str | None = None
    currency: str | None = None
    last_date_time_to_book: datetime.datetime | None = None
    last_date_time_to_purchase: datetime.datetime | None = None


class PricePenalty(CamelCaseBaseModel):
    passenger_type: enums.PassengerType
    information: list[PenaltyInformation]


class OfferPriceResponse(CamelCaseBaseModel):
    id: str  # noqa: A003
    information: booking.Information
    itinerary: offers.Offer
    docs: list[OfferPriceDoc] = pydantic.Field(default_factory=list)
    fare_rules: list[booking.FareRules]
    penalties: list[PricePenalty] = pydantic.Field(default_factory=list)
    extras: dict[str, Any]
    pricing_response_information: PricingResponseInformation
    has_finished: bool
    transaction_id: str


class AsyncOfferPriceResponse(CamelCaseBaseModel):
    id: str  # noqa: A003
    transaction_id: str
