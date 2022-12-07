"""Contains offer search request schemas."""
import datetime

import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.util import offer_enums, passenger_enums


class Trip(BaseSchema):
    """Trip schema."""

    origin: str = pydantic.Field(description="Departure airport", regex="[A-Z]{3}")
    destination: str = pydantic.Field(
        description="Arrival airport",
        regex="[a-zA-Z]{3}",
    )
    date: datetime.date = pydantic.Field(description="Departure date")
    time: datetime.time | None = pydantic.Field(description="Departure time")


class Passenger(BaseSchema):
    """Young Adult schema."""

    passenger_type: passenger_enums.PassengerTypeEnum = pydantic.Field(
        default=passenger_enums.PassengerTypeEnum.adult,
        description="Passenger type",
        alias="type",
    )
    birth_date: datetime.date = pydantic.Field(description="Birth date")


class OfferSearchRequest(BaseSchema):
    """Offer search request schema."""

    passengers: list[Passenger] = pydantic.Field(
        description="Passenger Item",
        min_items=1,
    )
    cabin_type: offer_enums.CabinTypeEnum = pydantic.Field(
        offer_enums.CabinTypeEnum.economy,
        description="Cabin type",
    )
    fare_preferences: set[offer_enums.FareGroupEnum] | None = pydantic.Field(
        description="Fare preferences",
        uniqueItems=True,
    )
    trips: list[Trip] = pydantic.Field(description="Trip list", min_items=1)
