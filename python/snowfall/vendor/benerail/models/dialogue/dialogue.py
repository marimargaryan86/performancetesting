from pydantic import Field

from snowfall.vendor.benerail.models import types
from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.train import TrainType
from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.trip_offers.enums import RequestedOfferParts


class DialogueIdTripFiltersParams(BenerailBaseModel):
    transfer_limit: float | None = Field(None, example=3)
    bike_transport: bool | None = None


class DialogueIdTripfiltersBody(BenerailBaseModel):
    origin: types.PlaceUrnStr
    destination: types.PlaceUrnStr
    via: list[types.PlaceUrnStr] | None = None
    train_types: list[TrainType] | None = None
    departure_date_time: types.ZonedDatetimeStr
    body_params: DialogueIdTripFiltersParams | None = Field(None, alias="params")


class DialogueIdTripOfferFiltersReturnTripParams(BenerailBaseModel):
    inward_date_time: str | None = Field(
        None,
        example="2021-08-04T10:20+01:00",
    )
    outward_offer_id: str | None = None


class DialogueIdTripofferfiltersBody(BenerailBaseModel):
    trip_filter_id: str | None = None
    passengers: list[str] | None = Field(None, description="array of passengerId's.")
    return_trip_params: DialogueIdTripOfferFiltersReturnTripParams | None = None
    market_segment: str | None = None
    requested_offer_parts: RequestedOfferParts | None = None


class Dialogue(BenerailBaseModel):
    identifier: str | None = Field(None, description="id of the dialogue", alias="id")
    external_id: str | None = Field(
        None,
        description="For consumer use. Field will not be evaluated.",
    )
    created_by: str | None = None
    created_at: str | None = Field(
        None,
        description="ISO-8601 timestamp showing date time and timezone",
    )
    modified_at: str | None = Field(
        None,
        description="ISO-8601 timestamp showing date time and timezone",
    )
    expires_at: str | None = Field(
        None,
        description="ISO-8601 timestamp showing date time and timezone",
    )
    passengers: list[ResourceLink] | None = None
    trip_filters: list[ResourceLink] | None = None
    trip_offer_filters: list[ResourceLink] | None = None
    booking: ResourceLink | None = None
    booker: ResourceLink | None = None
