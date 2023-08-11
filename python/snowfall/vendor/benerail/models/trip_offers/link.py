from pydantic import AnyUrl, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.trip_offers.summary import (
    OfferPartSummary,
    OfferSummary,
    PassengerResourceLinkSummary,
    ProductSummary,
    TripOfferSummary,
    TripSummary,
)


class TripOfferResourceLink(BenerailBaseModel):
    href: AnyUrl = Field(..., description="callable url")
    title: str = Field(
        ...,
        description="human-readable string representing the linked resource",
    )
    summary: TripOfferSummary | None = None


class TripResourceLink(BenerailBaseModel):
    href: AnyUrl
    title: str | None = Field(
        None,
        description="human-readable string representing the linked resource",
    )
    summary: TripSummary | None = None


class PassengerResourceLink(BenerailBaseModel):
    href: AnyUrl
    title: str | None = Field(
        None,
        description="human-readable string representing the linked resource",
    )
    summary: PassengerResourceLinkSummary | None = None


class ProductResourceLink(BenerailBaseModel):
    href: AnyUrl
    title: str | None = Field(
        None,
        description="human-readable string representing the linked resource",
    )
    summary: ProductSummary | None = None


class OfferResourceLink(BenerailBaseModel):
    href: AnyUrl
    title: str | None = Field(
        None,
        description="human-readable string representing the linked resource",
    )
    summary: OfferSummary | None = None


class OfferPartResourceLink(BenerailBaseModel):
    href: AnyUrl
    title: str | None = Field(
        None,
        description="human-readable string representing the linked resource",
    )
    summary: OfferPartSummary | None = None
