"""Contains order response schemas."""
import datetime
import uuid
from abc import ABC

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models import (
    response_common_offer_schemas,
    response_common_order_schemas,
    response_common_passenger_schemas,
)
from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.util import order_enums, passenger_enums


class OrderItem(BaseSchema, ABC):
    """Order item schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    order_item_type: order_enums.ServiceTypeEnum = pydantic.Field(
        description="Order item type",
        alias="type",
    )


class SegmentOrderItem(OrderItem):
    """Segment order item schema."""

    service_type: order_enums.ServiceTypeEnum = pydantic.Field(
        order_enums.ServiceTypeEnum.segment,
        const=True,
        description="Segment type",
        alias="type",
    )
    price: response_common_order_schemas.PriceDetailed = pydantic.Field(
        description="Price",
    )
    passenger_id: str = pydantic.Field(description="Passenger identifier")
    segment_ids: list[str] = pydantic.Field(description="Segment identifiers")
    penalty_ids: list[str] = pydantic.Field(description="Penalty identifiers")


class SeatOrderItem(OrderItem):
    """Seat order item schema."""

    seat_type: order_enums.ServiceTypeEnum = pydantic.Field(
        order_enums.ServiceTypeEnum.seat,
        const=True,
        description="Seat type",
        alias="type",
    )
    price: response_common_order_schemas.PriceSimple = pydantic.Field(
        description="Price",
    )
    number: str = pydantic.Field(description="Seat number")
    column: str = pydantic.Field(description="Seat column")
    passenger_id: str = pydantic.Field(description="Passenger identifier")
    segment_id: str = pydantic.Field(description="Segment identifier")


class BagOrderItem(OrderItem):
    """Bag order item schema."""

    bag_type: order_enums.ServiceTypeEnum = pydantic.Field(
        order_enums.ServiceTypeEnum.bag,
        const=True,
        description="Bag type",
        alias="type",
    )
    price: response_common_order_schemas.PriceSimple = pydantic.Field(
        description="Price",
    )
    description: list[str] = pydantic.Field(description="Description")
    passenger_id: str = pydantic.Field(description="Passenger identifier")


class Order(BaseSchema):
    """Order schema."""

    pnr: str = pydantic.Field(description="PNR")
    price: response_common_order_schemas.PriceSimple = pydantic.Field(
        description="Price",
    )
    order_items: list[SegmentOrderItem | SeatOrderItem | BagOrderItem] = pydantic.Field(
        description="Order items",
        alias="items",
    )


class Coupon(BaseSchema):
    """Coupon schema."""

    origin: str = pydantic.Field(description="Origin IATA")
    destination: str = pydantic.Field(description="Destination IATA")
    departure_at: datetime.datetime = pydantic.Field(description="Departure date time")
    fare_basis_code: str = pydantic.Field(description="Fare basis code")
    marketing_carrier: response_common_offer_schemas.Carrier = pydantic.Field(
        description="Marketing carrier",
    )


class Ticket(BaseSchema):
    """Ticket schema."""

    number: str = pydantic.Field(description="Ticker document number")
    ticket_type: order_enums.TicketTypeEnum = pydantic.Field(
        description="Type",
        alias="type",
    )
    issued_at: datetime.date = pydantic.Field(description="Date of issue")
    passenger_id: str = pydantic.Field(description="Passenger identifier")
    coupons: list[Coupon] = pydantic.Field(description="Coupons")


class Passenger(response_common_passenger_schemas.PassengerSimple):
    """Passenger schema."""

    first_name: str = pydantic.Field(description="First name")
    last_name: str = pydantic.Field(description="Last name")
    name_title: str = pydantic.Field(description="Name title")
    gender: passenger_enums.GenderEnum | None = pydantic.Field(description="Gender")
    birth_date: datetime.date | None = pydantic.Field(description="Birth date")
    contact: response_common_passenger_schemas.Contact | None = pydantic.Field(
        description="Contact information",
    )


class OrderResponse(BaseSchema):
    """Order response schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    payment_expires_at: datetime.datetime | None = pydantic.Field(
        description="Payment expiration date time",
    )
    tickets: list[Ticket] = pydantic.Field(description="Tickets")
    order: Order = pydantic.Field(description="Order")
    passengers: list[Passenger] = pydantic.Field(
        description="Passenger definitions",
    )
    segments: list[response_common_offer_schemas.Segment] = pydantic.Field(
        description="Segment definitions",
    )
    origin_destinations: list[response_common_order_schemas.OriginDestination] = (
        pydantic.Field(description="Origin destinations")
    )
    penalties: list[response_common_order_schemas.Penalty] = pydantic.Field(
        description="Penalty definitions",
    )
