from snowfall.project.junction.go.service.orders import orders
from snowfall.project.junction.go.service.orders.v1alpha import models_pb2
from snowfall.stdlib.transport.amqp import consumer, types


class BookingImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[models_pb2.Booking],
        booking_repository: orders.BookingRepository,
    ):
        self._consumer = consumer_obj
        self._bookings = booking_repository

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[models_pb2.Booking],
    ) -> None:
        await self._bookings.update(booking=message.body)
