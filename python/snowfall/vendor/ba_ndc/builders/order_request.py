from __future__ import annotations

import uuid

from snowfall.vendor.ba_ndc.models.request_order_schemas import (
    CreateOrderRequest,
    PassengerExtended,
)


class OrderRequestBuilder(object):
    def __init__(self, offer_id: uuid.UUID) -> None:
        self._passengers: list[PassengerExtended] = []
        self._offer_id: uuid.UUID = offer_id

    def add_passenger(self, passenger: PassengerExtended) -> OrderRequestBuilder:
        self._passengers.append(passenger)
        return self

    def build(self) -> CreateOrderRequest:
        return CreateOrderRequest(
            offer_id=self._offer_id,
            passengers=self._passengers,
            payment=None,
        )
