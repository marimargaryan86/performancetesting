from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.pay.adapter import quotations, transactions
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.stdlib.logging import stdout


class PayTransactionCreationError(Exception):
    """Raised when an error occurs creating a transaction in PAY."""


class PayTransactionCreator(object):
    def __init__(
        self,
        transactions_client: transactions.Client,
        quotations_client: quotations.Client,
        *,
        use_pay_to_create_transaction: bool,
    ):
        self._use_pay_to_create_transaction = use_pay_to_create_transaction
        self._transactions_client = transactions_client
        self._quotations_client = quotations_client
        self._logger = stdout.get_logger()

    async def create_transaction_and_set_id(
        self,
        booking: models_pb2.Booking,
    ) -> models_pb2.Booking:
        if self._use_pay_to_create_transaction:
            quotation = await self._get_quotation(
                quotation_id=booking.trip_option.pay_quote_id,
            )
            transaction = await self._create_transaction(
                quotation=quotation,
                external_reference=booking.id,
                invoice_reference=booking.trip_result.provider_booking_reference,
                order_id=booking.order_id,
            )
            await self._update_quotation_status(quotation)

            booking.transaction_id = transaction.id
        return booking

    async def _get_quotation(
        self,
        quotation_id: str,
    ) -> transactions_models_pb2.Quotation:
        try:
            return await self._quotations_client.get(identifier=quotation_id)
        except errors.NotFoundError as err:
            self._logger.exception(
                "Failed to fetch quotation in Pay",
                pay_quote_id=quotation_id,
            )
            raise PayTransactionCreationError from err

    async def _create_transaction(
        self,
        quotation: transactions_models_pb2.Quotation,
        external_reference: str,
        invoice_reference: str,
        order_id: str,
    ) -> transactions_models_pb2.Transaction:
        try:
            return await self._transactions_client.create(
                quotation=quotation,
                external_reference=external_reference,
                invoice_reference=invoice_reference,
                order_id=order_id,
            )
        except errors.UnhandledError as err:
            raise PayTransactionCreationError from err

    async def _update_quotation_status(
        self,
        quotation: transactions_models_pb2.Quotation,
    ) -> None:
        response = await self._quotations_client.update_status(
            identifier=quotation.id,
            status=transactions_models_pb2.QuotationStatus.QUOTATION_STATUS_CONFIRMED,
        )

        if not response:
            self._logger.exception(
                "Failed to update quotation status in Pay",
                pay_quote_id=quotation.id,
            )
