from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.trip_offers.summary import (
    OfferPartSummary,
    OfferSummary,
    PassengerResourceLinkSummary,
    ProductSummary,
    TripOfferSummary,
    TripSummary,
)


class TripOfferResourceLink(ResourceLink):
    summary: TripOfferSummary | None = None


class TripResourceLink(ResourceLink):
    summary: TripSummary | None = None


class PassengerResourceLink(ResourceLink):
    summary: PassengerResourceLinkSummary | None = None


class ProductResourceLink(ResourceLink):
    summary: ProductSummary | None = None


class OfferResourceLink(ResourceLink):
    summary: OfferSummary


class OfferPartResourceLink(ResourceLink):
    summary: OfferPartSummary | None = None
