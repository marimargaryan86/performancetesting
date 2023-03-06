import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.booking import Booking
from snowfall.vendor.benerail.models.customer import BookerResponse
from snowfall.vendor.benerail.models.dialogue import Dialogue
from snowfall.vendor.benerail.models.link import Link, ResourceLink
from snowfall.vendor.benerail.models.metadata import MetaData
from snowfall.vendor.benerail.models.passenger import Passenger
from snowfall.vendor.benerail.models.trip import TripFilter, TripOfferFilter


class GetBookingResponse(BenerailBaseModel):
    metadata: MetaData | None
    booking_result: Booking | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetBookerResponse(BenerailBaseModel):
    metadata: MetaData | None
    get_booker_result: BookerResponse | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetDialoguesResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: list[ResourceLink] | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetDialogueResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: Dialogue | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetPassengerResponse(BenerailBaseModel):
    metadata: MetaData | None
    passenger_result: Passenger | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetTripFilterResponse(BenerailBaseModel):
    metadata: MetaData | None
    trip_filter_result: TripFilter | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetTripOfferFilterResponse(BenerailBaseModel):
    metadata: MetaData | None
    trip_offer_filter_result: TripOfferFilter | None = pydantic.Field(
        ...,
        alias="result",
    )
    links: list[Link] | None
