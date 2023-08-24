from pydantic.v1 import AnyUrl

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.dialogue.summary import (
    BookerSummary,
    BookingSummary,
    TripFilterSummary,
    TripOfferFilterSummary,
)


class TripFilterResourceLink(BenerailBaseModel):
    href: AnyUrl | None = None
    title: str | None = None
    summary: TripFilterSummary | None = None


class TripOfferFilterResourceLink(BenerailBaseModel):
    href: AnyUrl | None = None
    title: str | None = None
    summary: TripOfferFilterSummary | None = None


class BookerResourceLink(BenerailBaseModel):
    href: AnyUrl | None = None
    title: str | None = None
    summary: BookerSummary | None = None


class BookingResourceLink(BenerailBaseModel):
    href: AnyUrl | None = None
    title: str | None = None
    summary: BookingSummary | None = None
