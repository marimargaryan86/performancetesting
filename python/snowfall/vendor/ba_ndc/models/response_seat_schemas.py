"""Contains seat response schemas."""
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


class Seat(BaseSchema):
    """Seat schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    row: str = pydantic.Field(description="Seat row")
    column: str = pydantic.Field(description="Seat column")
    passenger_ids: list[str] = pydantic.Field(description="Passenger identifiers")
    price: response_common_order_schemas.PriceSimple = pydantic.Field(
        description="Price",
    )
    row_characteristics: list[offer_enums.RowTypeEnum] = pydantic.Field(
        description="Row characteristics",
    )
    seat_characteristics: list[offer_enums.SeatTypeEnum] = pydantic.Field(
        description="Seat characteristics",
    )


class Cabin(BaseSchema):
    """Cabin schema."""

    cabin_type: offer_enums.CabinTypeEnum = pydantic.Field(
        description="Cabin type",
        alias="type",
    )
    seats: list[Seat] = pydantic.Field(description="Seats")


class SeatMap(BaseSchema):
    """Seat map schema."""

    cabins: list[Cabin] = pydantic.Field(description="Cabins")
    segment_id: str = pydantic.Field(description="Segment identifier")


class SeatsResponse(BaseSchema):
    """Seats response schema."""

    expires_at: datetime.datetime = pydantic.Field(
        description="Offer expiration date time",
    )
    price_guarantee_expires_at: datetime.datetime = pydantic.Field(
        description="Price guarantee expiration date time",
    )
    seat_maps: list[SeatMap] = pydantic.Field(description="Seat maps")
    passengers: list[response_common_passenger_schemas.PassengerSimple] = (
        pydantic.Field(
            description="Passenger definitions",
        )
    )
    disclosures: list[response_common_offer_schemas.Disclosure] = pydantic.Field(
        description="Disclosure definitions",
    )
    segments: list[response_common_offer_schemas.Segment] = pydantic.Field(
        description="Segment definitions",
    )
