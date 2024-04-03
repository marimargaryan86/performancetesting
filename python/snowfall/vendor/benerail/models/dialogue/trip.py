import datetime
from types import MappingProxyType

from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.train import TrainType1
from snowfall.vendor.benerail.models.dialogue.dialogue import (
    DialogueIdTripFiltersParams,
)
from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.place import Place


class TripFilter(BenerailBaseModel):
    class Config:
        json_encoders = MappingProxyType(
            {
                datetime.datetime: lambda dt: dt.isoformat(timespec="minutes"),
            },
        )

    identifier: str = Field(..., alias="id")
    origin: Place | None = None
    destination: Place | None = None
    via: list[Place] | None = None
    train_types: list[TrainType1] | None = None
    departure_date_time: datetime.datetime | None = None
    trip_collection: ResourceLink | None = None
    trip_filter_params: DialogueIdTripFiltersParams | None = Field(None, alias="params")
