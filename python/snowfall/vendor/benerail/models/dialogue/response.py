import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.dialogue.customer import BookerResponse
from snowfall.vendor.benerail.models.dialogue.dialogue import Dialogue
from snowfall.vendor.benerail.models.dialogue.passenger import Passenger
from snowfall.vendor.benerail.models.dialogue.trip import TripFilter
from snowfall.vendor.benerail.models.link import Link, ResourceLink
from snowfall.vendor.benerail.models.metadata import MetaData
from snowfall.vendor.benerail.models.trip_offers.trip_offers import TripOfferFilter


class GetBookerResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: BookerResponse | None = pydantic.Field(..., alias="result")
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
    response_result: Passenger | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetTripFilterResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: TripFilter | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetTripOfferFilterResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: TripOfferFilter | None = pydantic.Field(
        ...,
        alias="result",
    )
    links: list[Link] | None
