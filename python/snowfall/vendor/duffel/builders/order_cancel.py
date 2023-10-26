from __future__ import annotations

import pydantic

from snowfall.vendor.duffel.builders.base import DuffelRequestBaseModel


class OrderCancelRequestData(DuffelRequestBaseModel):
    order_id: str | None = None


class OrderCancelRequest(DuffelRequestBaseModel):
    order_data: OrderCancelRequestData = pydantic.Field(alias="data")


class OrderCancelRequestBuilder(object):
    def __init__(self) -> None:
        self._order_id: str | None = None

    def order_type(self, order_id: str) -> OrderCancelRequestBuilder:
        self._order_id = order_id
        return self

    def build(self) -> OrderCancelRequest:
        return OrderCancelRequest(
            order_data=OrderCancelRequestData(
                order_id=self._order_id,
            ),
        )
