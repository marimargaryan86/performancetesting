import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import Link
from snowfall.vendor.benerail.models.metadata import MetaData
from snowfall.vendor.benerail.models.trips.trips import Trip, TripCollection


class GetTripResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: Trip | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetTripCollectionResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: TripCollection | None = pydantic.Field(..., alias="result")
    links: list[Link] | None
