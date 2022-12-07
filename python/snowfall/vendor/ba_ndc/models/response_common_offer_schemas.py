import datetime

import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.response_common_order_schemas import Airport
from snowfall.vendor.ba_ndc.models.util import offer_enums


class Equipment(BaseSchema):
    """Equipment schema."""

    code: str = pydantic.Field(description="Aircraft code")
    name: str | None = pydantic.Field(description="Aircraft name")


class Carrier(BaseSchema):
    """Carrier schema."""

    airline_id: str = pydantic.Field(description="Airline identifier")
    airline_name: str | None = pydantic.Field(description="Airline name")
    flight_number: str | None = pydantic.Field(description="Flight number")


class Segment(BaseSchema):
    """Segment schema."""

    identifier: str = pydantic.Field(..., alias="id")
    origin: Airport = pydantic.Field(description="Origin airport")
    destination: Airport = pydantic.Field(description="Destination airport")
    departure_date_time: datetime.datetime = pydantic.Field(
        description="Date and time of departure (local)",
    )
    arrival_date_time: datetime.datetime = pydantic.Field(
        description="Date and time of arrival (local)",
    )
    duration: datetime.timedelta | None = pydantic.Field(description="Segment duration")
    equipment: Equipment | None = pydantic.Field(description="Segment aircraft")
    marketing_carrier: Carrier = pydantic.Field(description="Marketing carrier")
    operating_carrier: Carrier | None = pydantic.Field(description="Operating carrier")
    stop_count: int | None = pydantic.Field(description="Number of stops")


class FareGroup(BaseSchema):
    """Fare group schema."""

    identifier: str = pydantic.Field(..., alias="id")
    fare_group_type: offer_enums.FareGroupEnum = pydantic.Field(
        description="Fare group type",
        alias="type",
    )
    basis_code: str = pydantic.Field(description="Basis code")
    passenger_ids: list[str] = pydantic.Field(description="Passenger identifiers")


class ClassOfService(BaseSchema):
    """Class of service schema."""

    disclosure_id: str | None = pydantic.Field(description="Disclosure identifier")
    segment_id: str = pydantic.Field(description="Segment identifier")
    fare_group_id: str = pydantic.Field(description="Fare group identifier")
    seats_left: int | None = pydantic.Field(description="Number of seats left")


class PriceClass(BaseSchema):
    """Price class schema."""

    identifier: str = pydantic.Field(..., alias="id")
    cabin_type: offer_enums.CabinTypeEnum = pydantic.Field(description="Cabin type")
    name: str = pydantic.Field(description="Price class name")
    classes_of_service: list[ClassOfService] = pydantic.Field(
        description="Classes of service",
    )


class Disclosure(BaseSchema):
    """Disclosure schema."""

    identifier: str = pydantic.Field(..., alias="id")
    text: list[str] = pydantic.Field(description="Disclosure text")


class BagDisclosure(BaseSchema):
    """Bag disclosure schema."""

    identifier: str = pydantic.Field(..., alias="id")
    rule: list[str] = pydantic.Field(description="Bag disclosure rule")
    description: list[str] = pydantic.Field(description="Bag disclosure description")


class Trip(BaseSchema):
    """Trip schema."""

    duration: datetime.timedelta = pydantic.Field(description="Trip duration")
    price_class_id: str = pydantic.Field(description="Price class identifier")
    segment_ids: list[str] = pydantic.Field(description="Segment identifiers")
    penalty_ids: list[str] | None = pydantic.Field(description="Penalty identifiers")
