from __future__ import annotations

import uuid
from decimal import Decimal

from snowfall.vendor.ba_ndc.models.payer_details import Address, PayerDetailsPassenger
from snowfall.vendor.ba_ndc.models.request_order_schemas import (
    CashPayment,
    CreateOrderRequest,
    PassengerExtended,
)


class OrderRequestBuilder(object):
    def __init__(self, offer_id: uuid.UUID) -> None:
        self.residence_address: Address | None = None
        self._passengers: list[PassengerExtended] = []
        self._offer_id: uuid.UUID = offer_id
        self._payment: CashPayment | None = None

    def add_passenger(self, passenger: PassengerExtended) -> OrderRequestBuilder:
        self._passengers.append(passenger)
        return self

    def set_cash_payment_info(
        self,
        passenger_id: str,
        currency_code: str,
        amount: Decimal,
    ) -> OrderRequestBuilder:
        self._payment = CashPayment(
            payment_type="cash",
            currency_code=currency_code,
            amount=amount,
            payer_details=PayerDetailsPassenger(
                payer_details_type="passenger",
                passenger_id=passenger_id,
            ),
        )
        return self

    def build(self) -> CreateOrderRequest:
        return CreateOrderRequest(
            offer_id=self._offer_id,
            passengers=self._passengers,
            residence_address=self.residence_address,
            payment=self._payment,
        )
