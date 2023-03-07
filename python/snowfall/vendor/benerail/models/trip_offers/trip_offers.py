import datetime
from typing import Literal

import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.train import TrainType1
from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.place import Place
from snowfall.vendor.benerail.models.trip_offers.offer import BookableStatus, Message


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


class TripOffer(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    origin: Place
    destination: Place
    departure_at: datetime.datetime
    duration: str | None
    number_of_transfers: int | None
    trip: ResourceLink
    offers: list[ResourceLink] | None
    passengers: list[ResourceLink]
    bookable_status: BookableStatus


class TripOfferCollection(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    messages: list[Message] | None
    market_segment: str | None
    trip_offers: list[ResourceLink] | None
