import structlog

from snowfall.project.junction.go.service.offers import price_quotes
from snowfall.project.junction.go.service.orders import orders
from snowfall.project.junction.go.service.orders.pay_transactions import (
    PayTransactionCreationError,
    PayTransactionCreator,
)
from snowfall.project.junction.go.service.orders.v1alpha import models_pb2
from snowfall.stdlib.transport.amqp import consumer, types


class BookingImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[models_pb2.Booking],
        booking_repository: orders.BookingRepository,
        price_quote_repository: price_quotes.PriceQuoteRepository,
        pay_transaction_creator: PayTransactionCreator,
    ):
        self._consumer = consumer_obj
        self._bookings = booking_repository
        self._price_quotes = price_quote_repository
        self._logger = structlog.get_logger(__name__)
        self._pay_transaction_creator = pay_transaction_creator

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[models_pb2.Booking],
    ) -> None:
        await self._bookings.update(booking=message.body)

        price_quote = await self._price_quotes.find_by_id(
            message.body.trip_option.price_quote_id,
        )

        if price_quote:
            try:  # noqa:WPS229
                booking_with_transaction = (
                    await self._pay_transaction_creator.create_transaction_and_set_id(
                        message.body,
                        price_quote.pay_quote_id,
                    )
                )
                await self._bookings.update(booking=booking_with_transaction)
            except PayTransactionCreationError:
                # Only logging exceptions as we'd rather successful bookings
                self._logger.exception(
                    "Failed to create a transaction in Pay for booking",
                    booking_id=message.body.id,
                )
        else:
            self._logger.warning(
                "Unable to find price_quote for booking",
                booking_id=message.body.id,
                price_quote_id=message.body.trip_option.price_quote_id,
            )
