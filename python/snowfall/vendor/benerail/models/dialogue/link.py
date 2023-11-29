from snowfall.vendor.benerail.models.dialogue.summary import (
    BookerSummary,
    BookingSummary,
    TripFilterSummary,
    TripOfferFilterSummary,
)
from snowfall.vendor.benerail.models.link import ResourceLink


class TripFilterResourceLink(ResourceLink):
    summary: TripFilterSummary | None = None


class TripOfferFilterResourceLink(ResourceLink):
    summary: TripOfferFilterSummary | None = None


class BookerResourceLink(ResourceLink):
    summary: BookerSummary | None = None


class BookingResourceLink(ResourceLink):
    summary: BookingSummary | None = None
