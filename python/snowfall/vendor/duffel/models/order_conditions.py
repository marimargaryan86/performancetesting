from snowfall.vendor.duffel.models.base import DuffelBaseModel


class OrderConditionChangeBeforeDeparture(DuffelBaseModel):
    allowed: bool
    penalty_amount: str | None
    penalty_currency: str | None


class OrderConditionRefundBeforeDeparture(DuffelBaseModel):
    allowed: bool
    penalty_amount: str | None
    penalty_currency: str | None


class OrderConditions(DuffelBaseModel):
    change_before_departure: OrderConditionChangeBeforeDeparture | None
    refund_before_departure: OrderConditionRefundBeforeDeparture | None
