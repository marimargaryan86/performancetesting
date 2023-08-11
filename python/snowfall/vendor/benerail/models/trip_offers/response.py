from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import Link
from snowfall.vendor.benerail.models.metadata import Metadata
from snowfall.vendor.benerail.models.trip_offers.offer import Offer, OfferPart
from snowfall.vendor.benerail.models.trip_offers.trip_offers import (
    TripOffer,
    TripOfferCollection,
)


class GetOfferPartResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: OfferPart | None = Field(None, alias="result")
    links: list[Link] | None = None


class GetOfferResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: Offer = Field(..., alias="result")
    links: list[Link] | None = None


class GetTripOfferResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: TripOffer = Field(..., alias="result")
    links: list[Link] | None = None


class GetTripOfferCollectionResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: TripOfferCollection = Field(..., alias="result")
    links: list[Link]
