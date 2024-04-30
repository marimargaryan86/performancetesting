from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.pay.adapter import transactions
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.stdlib.logging import stdout


class PayTransactionCreationError(Exception):
    """Raised when an error occurs creating a transaction in PAY."""


class PayTransactionCreator:
    def __init__(
        self,
        transactions_client: transactions.Client,
        *,
        use_pay_to_create_transaction: bool,
    ):
        self._use_pay_to_create_transaction = use_pay_to_create_transaction
        self._transactions_client = transactions_client
        self._logger = stdout.get_logger()

    async def create_transaction(
        self,
        booking: models_pb2.Booking,
    ) -> str:
        if self._use_pay_to_create_transaction:
            transaction = await self._create_transaction(
                quotation_id=booking.trip_option.pay_quote_id,
                external_reference=booking.id,
                invoice_reference=booking.trip_result.provider_booking_reference,
                order_id=booking.order_id,
            )
            return transaction.id

        return ""

    async def _create_transaction(
        self,
        quotation_id: str,
        external_reference: str,
        invoice_reference: str,
        order_id: str,
    ) -> transactions_models_pb2.Transaction:
        try:
            return await errors.handle_grpc_errors(
                self._transactions_client.create(
                    quotation_id=quotation_id,
                    external_reference=external_reference,
                    invoice_reference=invoice_reference,
                    order_id=order_id,
                ),
            )
        except (errors.UnhandledError, errors.NotFoundError) as err:
            self._logger.exception(
                "Transaction creation failed",
                pay_quote_id=quotation_id,
                external_reference=external_reference,
                order_id=order_id,
            )
            raise PayTransactionCreationError from err
