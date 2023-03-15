from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import Link
from snowfall.vendor.benerail.models.metadata import Metadata
from snowfall.vendor.benerail.models.trips.trips import Trip, TripCollection


class GetTripResponse(BenerailBaseModel):
    metadata: Metadata | None
    response_result: Trip | None = Field(..., alias="result")
    links: list[Link] | None


class GetTripCollectionResponse(BenerailBaseModel):
    metadata: Metadata | None
    response_result: TripCollection | None = Field(..., alias="result")
    links: list[Link] | None
