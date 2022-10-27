import datetime
from typing import Any, Optional

from snowfall.vendor.ask2go import enums
from snowfall.vendor.ask2go.models import booking, offers
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class OfferPriceDoc(CamelCaseBaseModel):
    doc_type: str
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
    changeable: Optional[bool]
    refundable: bool
    applicability: enums.Applicability
    amount: Optional[str]
    currency: Optional[str]
    last_date_time_to_book: Optional[datetime.datetime]
    last_date_time_to_purchase: Optional[datetime.datetime]


class PricePenalty(CamelCaseBaseModel):
    passenger_type: enums.PassengerType
    information: list[PenaltyInformation]


class OfferPriceResponse(CamelCaseBaseModel):
    id: str  # noqa: A003
    information: booking.Information
    itinerary: offers.Offer
    docs: list[OfferPriceDoc]
    fare_rules: list[booking.FareRules]
    penalties: Optional[list[PricePenalty]]
    extras: dict[str, Any]
    pricing_response_information: PricingResponseInformation
    has_finished: bool
    transaction_id: str


class AsyncOfferPriceResponse(CamelCaseBaseModel):
    id: str  # noqa: A003
    transaction_id: str
