import datetime

import pydantic

from snowfall.vendor.currency_cloud.models.base import CamelCaseBaseModel


class Payment(CamelCaseBaseModel):
    currency: str
    beneficiary_id: str
    amount: str
    reason: str
    reference: str
    unique_request_id: str
    payment_type: str
    payment_date: datetime.datetime | None = None


class PaymentRequest(Payment):
    """Payment request  model."""


class PaymentResponse(Payment):
    identifier: str = pydantic.Field(..., alias="id")
