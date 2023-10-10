from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.train import TrainType1
from snowfall.vendor.benerail.models.place import Place
from snowfall.vendor.benerail.models.trip_offers.link import TripResourceLink


class TripCo2Info(BenerailBaseModel):
    co2_amount: float | None = Field(None, description="Kilogram of CO2")
    eco_checker_url: str | None = Field(
        None,
        description="URL",
        example="http://demo.hafas.de/bin/pub/bene/eco/query.exe/...",
    )


class TransferLeg(BenerailBaseModel):
    leg_type: str = Field(..., description="transferLeg", alias="type")
    seq_id: float
    origin: Place
    destination: Place
    duration: str = Field(..., description="ISO-8601 period.", example="PT11M")


class TimedLeg(BenerailBaseModel):
    leg_type: str = Field(..., description="TimedLeg", alias="type")
    seq_id: float
    origin: Place
    destination: Place
    departure_at: str = Field(
        ...,
        description="ISO-8601 timestamp showing date time and timezone",
    )
    arrival_at: str = Field(
        ...,
        description="ISO-8601 timestamp showing date time and timezone",
    )
    duration: str = Field(..., description="ISO-8601 period.", example="PT25M")
    train_type: TrainType1 | None = None
    train_numbers: list[str] | None = None


class Trip(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    duration: str | None = Field(
        None,
        description="Overall duration of the trip",
        example="PT20M",
    )
    origin: Place
    destination: Place
    departure_at: str = Field(
        ...,
        description="ISO-8601 timestamp showing date time and timezone of departure",
        example="2021-09-29T13:20:34.143+02:00",
    )
    arrival_at: str = Field(
        ...,
        description="ISO-8601 timestamp showing date time and timezone of arrival",
        example="2021-09-29T13:20:34.143+02:00",
    )
    number_of_transfers: float | None = Field(
        None,
        description="Number of interchanges",
        example=1,
    )
    co2_info: TripCo2Info | None = None
    trip_legs: list[TimedLeg | TransferLeg]


class TripCollection(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    trips: list[TripResourceLink] | None = None
