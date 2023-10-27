"""Contains priced offer response schemas."""

import datetime
import uuid

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models import (
    response_common_offer_schemas,
    response_common_order_schemas,
    response_common_passenger_schemas,
)
from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.util import offer_enums


class Dimension(BaseSchema):
    """Dimension schema."""

    unit: offer_enums.DimensionUnitEnum
    height: float = pydantic.Field(description="Max height")
    length: float = pydantic.Field(description="Max length")
    width: float = pydantic.Field(description="Max width")


class Weight(BaseSchema):
    """Weight schema."""

    unit: offer_enums.WeightUnitEnum = pydantic.Field(description="Unit of measurement")
    weight_value: float = pydantic.Field(description="Max weight", alias="value")


class Measurement(BaseSchema):
    """Measurement schema."""

    dimensions: list[Dimension] = pydantic.Field(description="Measurement dimension")
    weight: list[Weight] = pydantic.Field(description="Measurement height")


class BagPieceAllowance(BaseSchema):
    """Bag piece allowance schema."""

    combination: offer_enums.BagPieceAllowanceCombinationEnum | None = pydantic.Field(
        description="Piece combination",
    )
    description: str = pydantic.Field(description="Piece description")
    quantity: int = pydantic.Field(description="Max quantity per passenger")
    passenger_ids: list[str] = pydantic.Field(
        description="Eligible passenger identifiers",
    )
    measurement: Measurement = pydantic.Field(description="Piece measurement")


class BagAllowance(BaseSchema):
    """Bag allowance schema."""

    identifier: str = pydantic.Field(..., alias="id")
    category: offer_enums.BagCategoryEnum = pydantic.Field(
        description="Bag allowance category",
    )
    piece_allowance: list[BagPieceAllowance] = pydantic.Field(
        description="Piece allowance list",
    )


class TripDetailed(response_common_offer_schemas.Trip):
    """Trip detailed schema."""

    penalty_ids: list[str] = pydantic.Field(description="Penalty identifiers")


class Bag(BaseSchema):
    """Bag schema."""

    bag_allowance_id: str = pydantic.Field(description="Bag allowance identifier")
    flight_ids: list[str] = pydantic.Field(description="Flight identifiers")
    passenger_ids: list[str] = pydantic.Field(description="Passenger identifiers")


class Offer(BaseSchema):
    """Offer schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    price: response_common_order_schemas.PriceDetailed = pydantic.Field(
        description="Offer price",
    )
    trips: list[TripDetailed] = pydantic.Field(
        description="Offer trips",
    )
    offer_items: list[response_common_order_schemas.OfferItem] = pydantic.Field(
        description="Offer items",
        alias="items",
    )
    bags: list[Bag] = pydantic.Field(description="Allowed baggage")
    bag_disclosure_ids: list[str] = pydantic.Field(
        description="Bag disclosure identifiers",
    )


class PricedOfferResponse(BaseSchema):
    """Priced offer response schema."""

    expires_at: datetime.datetime = pydantic.Field(
        description="Offer expiration date time",
    )
    payment_expires_at: datetime.datetime = pydantic.Field(
        description="payment expiration date time",
    )
    price_guarantee_expires_at: datetime.datetime = pydantic.Field(
        description="Price guarantee expiration date time",
    )
    offer: Offer = pydantic.Field(description="Offer details")
    passengers: list[response_common_passenger_schemas.PassengerSimple] = (
        pydantic.Field(
            description="Passenger definitions",
        )
    )
    segments: list[response_common_offer_schemas.Segment] = pydantic.Field(
        description="Journey segment definitions",
    )
    price_classes: list[response_common_offer_schemas.PriceClass] = pydantic.Field(
        description="Price class definitions",
    )
    flights: list[response_common_order_schemas.Flight] = pydantic.Field(
        description="Flight definitions",
    )
    fare_groups: list[response_common_offer_schemas.FareGroup] = pydantic.Field(
        description="Fare group definitions",
    )
    disclosures: list[response_common_offer_schemas.Disclosure] = pydantic.Field(
        description="Disclosure definitions",
    )
    bag_disclosures: list[response_common_offer_schemas.BagDisclosure] = pydantic.Field(
        description="Bag disclosure definitions",
    )
    bag_allowances: list[BagAllowance] = pydantic.Field(
        description="Bag allowance definitions",
    )
    penalties: list[response_common_order_schemas.Penalty] = pydantic.Field(
        description="Penalty definitions",
    )
    payment_cards: list[response_common_passenger_schemas.PaymentCard] = pydantic.Field(
        description="Payment card definitions",
    )
