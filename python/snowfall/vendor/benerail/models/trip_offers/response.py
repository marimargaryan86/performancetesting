import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import Link
from snowfall.vendor.benerail.models.metadata import MetaData
from snowfall.vendor.benerail.models.trip_offers.offer import Offer, OfferPart
from snowfall.vendor.benerail.models.trip_offers.trip_offers import (
    TripOffer,
    TripOfferCollection,
)


class GetBookedOfferResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: OfferPart | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetOfferResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: Offer | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetTripOfferResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: TripOffer | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetTripOfferCollectionResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: TripOfferCollection | None = pydantic.Field(..., alias="result")
    links: list[Link] | None
