from pydantic import AnyUrl, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.summary import (
    OrderSummary,
    PassengerResourceLinkSummary,
)


class OrderResourceLink(BenerailBaseModel):
    href: AnyUrl | None = None
    title: str | None = None
    summary: OrderSummary | None = None


class PassengerResourceLink(BenerailBaseModel):
    href: AnyUrl | None = Field(None, description="callable url")
    title: str | None = Field(
        None,
        description="human-readable string representing the linked resource",
    )
    summary: PassengerResourceLinkSummary | None = None
