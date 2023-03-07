import datetime
from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.train import TrainType
from snowfall.vendor.benerail.models.link import ResourceLink


class DialogueIdTripFiltersParams(BenerailBaseModel):
    transfer_limit: int | None
    bike_transport: bool | None


class DialogueIdTripFiltersBody(BenerailBaseModel):
    origin: str
    destination: str
    via: list[str] | None
    train_types: list[TrainType] | None
    departure_date_time: datetime.datetime | None
    body_params: DialogueIdTripFiltersParams | None = pydantic.Field(
        ...,
        alias="params",
    )


class DialogueIdTripOfferFiltersReturnTripParams(BenerailBaseModel):
    inward_date_time: datetime.datetime | None
    outward_offer_id: str | None


class DialogueIdTripOfferFiltersBody(BenerailBaseModel):
    trip_filter_id: str | None
    passengers: list[str] | None
    return_trip_params: DialogueIdTripOfferFiltersReturnTripParams | None
    market_segment: str | None
    requested_offer_parts: Literal[
        "admission-and-reservation",
        "reservation-only",
        "admission-only",
    ] | None


class Dialogue(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    external_id: str | None
    created_by: str | None
    created_at: datetime.datetime | None
    modified_at: datetime.datetime | None
    expires_at: datetime.datetime | None
    passengers: list[ResourceLink] | None
    trip_filters: list[ResourceLink] | None
    trip_offer_filters: list[ResourceLink] | None
    booking: ResourceLink | None
    booker: ResourceLink | None
