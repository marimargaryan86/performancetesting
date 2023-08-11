from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import ResourceLink
from snowfall.vendor.benerail.models.products.enums import OrderStates


class Order(BenerailBaseModel):
    identifier: str = Field(..., alias="id")
    booking_id: str | None = None
    payment_initiated: bool | None = None
    state: OrderStates | None = None
    selected_offers: list[ResourceLink] | None = None
    booked_offers: list[ResourceLink] | None = None
    payment: list[ResourceLink] | None = None


class OrderIdBody(BenerailBaseModel):
    state: OrderStates


class OrderIdRefundOffersBody(BenerailBaseModel):
    fulfillment_ids: list[str]
