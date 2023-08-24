from pydantic.v1 import Field

from snowfall.vendor.benerail.models import types
from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.train import TrainType1
from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.place import Place
from snowfall.vendor.benerail.models.trip_offers.enums import RequestedOfferParts
from snowfall.vendor.benerail.models.trip_offers.features import BookableStatus
from snowfall.vendor.benerail.models.trip_offers.link import (
    OfferResourceLink,
    PassengerResourceLink,
    TripOfferResourceLink,
    TripResourceLink,
)
from snowfall.vendor.benerail.models.trip_offers.offer import Message


class TripOfferFilter(BenerailBaseModel):
    identifier: str = Field(..., alias="id")
    origin: Place | None = None
    destination: Place | None = None
    departure_date_time: str | None = None
    train_types: list[TrainType1] | None = None
    market_segment: str | None = None
    requested_offer_parts: RequestedOfferParts | None = None
    inward_date_time: str | None = None
    outward_offer: ResourceLink | None = None
    trip_offer_collection: ResourceLink | None = None
    passengers: list[ResourceLink] | None = None


class TripOffer(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    origin: Place
    destination: Place
    departure_at: types.ZonedDatetimeStr
    duration: str | None = Field(
        None,
        description="Overall duration of the trip",
        example="PT20M",
    )
    number_of_transfers: int | None = Field(
        None,
        description="number of transfers",
        example=1,
    )
    trip: TripResourceLink
    offers: list[OfferResourceLink]
    passengers: list[PassengerResourceLink]
    bookable_status: BookableStatus | None = None


class TripOfferCollection(BenerailBaseModel):
    identifier: str | None = Field(None, alias="id")
    messages: list[Message] | None = None
    market_segment: str | None = None
    trip_offers: list[TripOfferResourceLink] | None = None
