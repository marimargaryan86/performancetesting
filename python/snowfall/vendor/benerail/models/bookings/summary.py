from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.payment import Price
from snowfall.vendor.benerail.models.products import enums


class OrderSummary(BenerailBaseModel):
    total_price: Price | None = None
    state: enums.OrderStates | None = None


class PassengerResourceLinkSummary(BenerailBaseModel):
    first_name: str | None = None
    last_name: str | None = None
