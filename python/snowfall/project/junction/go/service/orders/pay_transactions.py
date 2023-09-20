import httpx

from snowfall.project.junction.go.service.orders.pay_transactions_models import (
    PayTransactionResponse,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.vendor.junction.pay.client import Client as PayClient


class PayTransactionCreationError(Exception):
    """Raised when an error occurs creating a transaction in PAY."""


class PayTransactionCreator(object):
    def __init__(
        self,
        pay_client: PayClient,
        *,
        use_pay_to_create_transaction: bool,
    ):
        self._use_pay_to_create_transaction = use_pay_to_create_transaction
        self._pay_client = pay_client

    async def create_transaction_and_set_id(
        self,
        booking: models_pb2.Booking,
    ) -> models_pb2.Booking:
        if self._use_pay_to_create_transaction:
            transaction = await self._create_transaction(
                quotation_id=booking.trip_option.pay_quote_id,
                external_reference=booking.id,
                invoice_reference=booking.trip_result.provider_booking_reference,
                order_id=booking.order_id,
            )
            booking.transaction_id = transaction.data.id
        return booking

    async def _create_transaction(
        self,
        quotation_id: str,
        external_reference: str,
        invoice_reference: str,
        order_id: str,
    ) -> PayTransactionResponse:
        try:  # noqa: WPS229
            resp = await self._pay_client.create_transactions(
                external_reference=external_reference,
                invoice_reference=invoice_reference,
                quotation_id=quotation_id,
                order_id=order_id,
            )
            return PayTransactionResponse(**resp)
        except httpx.HTTPError as ex:
            raise PayTransactionCreationError from ex
