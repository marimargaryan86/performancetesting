import datetime

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.train import TrainType1
from snowfall.vendor.benerail.models.dialogue.dialogue import (
    DialogueIdTripFiltersParams,
)
from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.place import Place


class TripFilter(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    origin: Place | None
    destination: Place | None
    via: list[Place] | None
    train_types: list[TrainType1] | None
    departure_date_time: datetime.datetime | None
    trip_collection: ResourceLink | None
    trip_filter_params: DialogueIdTripFiltersParams | None = pydantic.Field(
        ...,
        alias="params",
    )
