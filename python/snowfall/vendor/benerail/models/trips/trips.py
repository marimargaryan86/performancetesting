import datetime

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.train import TrainType
from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.place import Place


class TripCo2Info(BenerailBaseModel):
    co2_amount: int | None
    eco_checker_url: str | None


class TransferLeg(BenerailBaseModel):
    transfer_leg_type: str = pydantic.Field(..., alias="type")
    seq_id: int
    origin: Place
    destination: Place
    duration: str


class TimedLeg(BenerailBaseModel):
    timed_leg_type: str = pydantic.Field(..., alias="type")
    seq_id: int
    origin: Place
    destination: Place
    departure_at: datetime.datetime
    arrival_at: datetime.datetime
    duration: str
    train_type: TrainType | None
    train_numbers: list[str] | None


class Trip(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    duration: str | None
    origin: Place
    destination: Place
    departure_at: datetime.datetime
    arrival_at: datetime.datetime
    number_of_transfers: int | None
    co2_info: TripCo2Info | None
    trip_legs: list[TimedLeg | TransferLeg] | None


class TripCollection(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    trips: list[ResourceLink] | None
