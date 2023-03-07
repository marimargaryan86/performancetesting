import pydantic

from snowfall.vendor.benerail.enums import OrderStates
from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import ResourceLink


class Order(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    booking_id: str | None
    payment_initiated: bool | None
    state: OrderStates | None
    selected_offers: list[ResourceLink] | None
    booked_offers: list[ResourceLink] | None
    payments: list[ResourceLink] | None


class OrderIdBody(BenerailBaseModel):
    state: OrderStates | None
