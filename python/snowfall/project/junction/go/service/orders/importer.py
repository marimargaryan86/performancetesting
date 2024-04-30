from snowfall.project.junction.go.service.orders import orders
from snowfall.project.junction.go.service.orders.pay_transactions import (
    PayTransactionCreationError,
    PayTransactionCreator,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types


class BookingImporter:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[models_pb2.Booking],
        booking_repository: orders.BookingRepository,
        pay_transaction_creator: PayTransactionCreator,
    ):
        self._consumer = consumer_obj
        self._bookings = booking_repository
        self._logger = stdout.get_logger()
        self._pay_transaction_creator = pay_transaction_creator

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[models_pb2.Booking],
    ) -> None:
        await self._bookings.update(booking=message.body)

        if message.body.trip_option.pay_quote_id:
            try:  # noqa: WPS229
                booking_with_transaction = message.body
                transaction_id = await self._pay_transaction_creator.create_transaction(
                    message.body,
                )
                booking_with_transaction.transaction_id = transaction_id
                await self._bookings.update(booking=booking_with_transaction)
            except PayTransactionCreationError:
                # Only logging exceptions as we'd rather successful bookings
                self._logger.exception(
                    "Failed to create a transaction in Pay for booking",
                    booking_id=message.body.id,
                    pay_quote_id=message.body.trip_option.pay_quote_id,
                )
