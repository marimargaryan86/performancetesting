"""Contains offer search response schemas."""

import datetime
import uuid

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models import (
    response_common_offer_schemas,
    response_common_order_schemas,
    response_common_passenger_schemas,
    response_priced_offer_schemas,
)
from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema


class Offer(BaseSchema):
    """Offer schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    price: response_common_order_schemas.PriceDetailed = pydantic.Field(
        description="Offer price",
    )
    trips: list[response_common_offer_schemas.Trip] = pydantic.Field(
        description="Offer trips",
    )


class OfferSearchResponse(BaseSchema):
    """Offer search response schema."""

    expires_at: datetime.datetime = pydantic.Field(
        description="Offer expiration date time",
    )
    payment_expires_at: datetime.datetime = pydantic.Field(
        description="payment expiration date time",
    )
    price_guarantee_expires_at: datetime.datetime | None = pydantic.Field(
        description="Price guarantee expiration date time",
    )
    offers: list[Offer] = pydantic.Field(description="Offers matching search criteria")
    passengers: list[
        response_common_passenger_schemas.PassengerSimple
    ] = pydantic.Field(
        description="Passenger definitions",
    )
    segments: list[response_common_offer_schemas.Segment] = pydantic.Field(
        description="Segment definitions",
    )
    price_classes: list[response_common_offer_schemas.PriceClass] = pydantic.Field(
        description="Price class definitions",
    )
    fare_groups: list[response_common_offer_schemas.FareGroup] = pydantic.Field(
        description="Fare group definitions",
    )
    disclosures: list[response_common_offer_schemas.Disclosure] = pydantic.Field(
        description="Disclosure definitions",
    )
    penalties: list[response_common_order_schemas.Penalty] = pydantic.Field(
        description="Penalty definitions",
    )
    bag_allowances: list[response_priced_offer_schemas.BagAllowance] = pydantic.Field(
        description="Bag allowance definitions",
    )
