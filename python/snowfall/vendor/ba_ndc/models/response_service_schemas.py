"""Contains service response schemas."""
import datetime
import uuid

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models import (
    response_common_offer_schemas,
    response_common_order_schemas,
    response_common_passenger_schemas,
)
from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.util import order_enums


class ServiceCombination(BaseSchema):
    """Service combination schema."""

    rule: order_enums.ServiceCombinationRuleEnum = pydantic.Field(
        description="Rule type",
    )
    offer_ids: list[uuid.UUID] = pydantic.Field(description="Offer identifiers")


class Offer(BaseSchema):
    """Offer schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    name: str = pydantic.Field(description="Service Name")
    service_type: order_enums.ServiceTypeEnum = pydantic.Field(
        description="Service type",
        alias="type",
    )
    price: response_common_order_schemas.PriceSimple = pydantic.Field(
        description="Service price",
    )
    max_quantity: int | None = pydantic.Field(
        description="Maximum quantity per passenger",
    )
    description: list[str] = pydantic.Field(description="Service description")
    combinations: list[ServiceCombination] = pydantic.Field(
        description="Service offer combinations",
    )
    passenger_ids: list[str] = pydantic.Field(
        description="Eligible passenger identifiers",
    )
    segment_ids: list[str] = pydantic.Field(description="Segment identifiers")


class ServicesResponse(BaseSchema):
    """Services response schema."""

    expires_at: datetime.datetime = pydantic.Field(
        description="Services expiration date time",
    )
    price_guarantee_expires_at: datetime.datetime = pydantic.Field(
        description="Services price guarantee expiration date time",
    )
    offers: list[Offer] = pydantic.Field(description="Service offers")
    passengers: list[response_common_passenger_schemas.PassengerSimple] = (
        pydantic.Field(
            description="Passenger definitions",
        )
    )
    segments: list[response_common_offer_schemas.Segment] = pydantic.Field(
        description="Segment definitions",
    )
    payment_cards: list[response_common_passenger_schemas.PaymentCard] = pydantic.Field(
        description="Payment card definitions",
    )
