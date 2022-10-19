from typing import Optional

import pydantic

from snowfall.vendor.ask2go.models import offers
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class PricingInformation(CamelCaseBaseModel):
    base: offers.PricingInformationBase


class BrandedFare(CamelCaseBaseModel):
    base_fare: str
    total_tax: str
    currency: str
    ticketing_cost: str
    fare_basis: list[str]
    is_refundable: bool
    brand_id: str
    brand_name: str


class ValidatedOfferItinerary(CamelCaseBaseModel):
    identifier: str = pydantic.Field(alias="id")
    is_refundable: bool
    docs_required: Optional[bool]
    gds: str
    direction: str
    trips: list[offers.Trip]
    pricing_information: PricingInformation
    passenger_pricing: list[offers.PassengerPricing]
    branded_fares: list[BrandedFare]


class ValidatedOfferResponse(CamelCaseBaseModel):
    itinerary: ValidatedOfferItinerary
