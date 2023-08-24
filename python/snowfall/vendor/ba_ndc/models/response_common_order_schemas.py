import datetime
from abc import ABC

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.util import order_enums


class Price(BaseSchema, ABC):
    """Price schema."""

    currency: str = pydantic.Field(description="Currency code")


class PriceSimple(Price):
    """Price simple schema."""

    total_amount: str = pydantic.Field(description="Total amount")


class PriceDetailed(Price):
    """Price detailed schema."""

    total_amount: str = pydantic.Field(description="Total amount")
    base_amount: str = pydantic.Field(description="Base amount")
    tax_amount: str = pydantic.Field(description="Tax amount")


class StopLocation(BaseSchema):
    airport_code: str = pydantic.Field(description="Airline identifier")
    arrival_date_time: datetime.datetime = pydantic.Field(
        description="Date and time of arrival stop (local)",
    )
    departure_date_time: datetime.datetime = pydantic.Field(
        description="Date and time of departure stop (local)",
    )


class Airport(BaseSchema):
    """Airport schema."""

    code: str = pydantic.Field(description="Airport IATA code")
    name: str | None = pydantic.Field(description="Airport name")
    terminal_gate: str | None = pydantic.Field(description="Terminal gate")
    terminal_name: str | None = pydantic.Field(description="Terminal name")


class Penalty(BaseSchema):
    """Penalty schema."""

    identifier: str = pydantic.Field(..., alias="id")
    penalty_type: order_enums.PenaltyTypeEnum = pydantic.Field(
        description="Type",
        alias="type",
    )
    price: PriceSimple | None = pydantic.Field(description="Penalty price")
    passenger_ids: list[str] = pydantic.Field(description="Passenger identifiers")
    remarks: list[str] = pydantic.Field(description="Penalty remarks")


class OfferItem(BaseSchema):
    """Offer item schema."""

    price: PriceDetailed = pydantic.Field(description="Journey price")
    passenger_ids: list[str] = pydantic.Field(description="Passenger identifiers")


class Flight(BaseSchema):
    """Flight schema."""

    identifier: str = pydantic.Field(..., alias="id")
    duration: datetime.timedelta | None = pydantic.Field(description="Flight duration")
    segment_ids: list[str] = pydantic.Field(description="Segment identifiers")


class OriginDestination(BaseSchema):
    identifier: str = pydantic.Field(..., alias="id")
    origin: Airport = pydantic.Field(description="Origin airport code")
    destination: Airport = pydantic.Field(description="Destination airport code")
    departure_date_time: datetime.datetime = pydantic.Field(
        description="Departure datetime",
    )
    arrival_date_time: datetime.datetime = pydantic.Field(
        description="Arrival datetime",
    )
    flights: list[Flight] = pydantic.Field(
        description="Flights of the origin destination",
    )
