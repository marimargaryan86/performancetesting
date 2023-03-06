import datetime
from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.dialogue import DialogueIdTripFiltersParams
from snowfall.vendor.benerail.models.link import ResourceLink, TrainType1
from snowfall.vendor.benerail.models.place import Place


class TripCollection(BenerailBaseModel):
    href: str | None
    title: str | None


class TripFilter(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    origin: Place | None
    destination: Place | None
    via: list[Place] | None
    train_types: list[TrainType1] | None
    departure_date_time: datetime.datetime | None
    trip_collection: TripCollection | None
    trip_filter_params: DialogueIdTripFiltersParams | None = pydantic.Field(
        ...,
        alias="params",
    )


class TripOfferFilter(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    origin: Place | None
    destination: Place | None
    departure_date_time: datetime.datetime | None
    train_types: list[TrainType1] | None
    mark_segment: str | None
    requested_offer_parts: Literal[
        "admission-and-reservation",
        "reservation-only",
        "admission-only",
    ] | None
    inward_date_time: str | None
    outward_offer: ResourceLink | None
    trip_offer_collection: ResourceLink | None
    passengers: list[ResourceLink] | None
