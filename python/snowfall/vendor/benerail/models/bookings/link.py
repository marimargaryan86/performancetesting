from snowfall.vendor.benerail.models.bookings.summary import (
    OrderSummary,
    PassengerResourceLinkSummary,
)
from snowfall.vendor.benerail.models.link import ResourceLink


class OrderResourceLink(ResourceLink):
    summary: OrderSummary | None = None


class PassengerResourceLink(ResourceLink):
    summary: PassengerResourceLinkSummary | None = None
