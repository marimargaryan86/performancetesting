from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.train import TrainType1
from snowfall.vendor.benerail.models.dialogue.dialogue import (
    DialogueIdTripFiltersParams,
)
from snowfall.vendor.benerail.models.link import ResourceLink, ZonedDateTime
from snowfall.vendor.benerail.models.place import Place


class TripFilter(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    origin: Place | None = None
    destination: Place | None = None
    via: list[Place] | None = None
    train_types: list[TrainType1] | None = None
    departure_date_time: ZonedDateTime | None = None
    trip_collection: ResourceLink | None = None
    trip_filter_params: DialogueIdTripFiltersParams | None = Field(None, alias="params")
