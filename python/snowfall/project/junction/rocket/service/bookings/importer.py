from snowfall.project.junction.rocket.service.bookings import repository
from snowfall.project.junction.rocket.service.bookings.v1alpha import models_pb2
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types


class BookingImporter:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[models_pb2.Booking],
        booking_repository: repository.BookingRepository,
    ):
        self._consumer = consumer_obj
        self._bookings = booking_repository
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[models_pb2.Booking],
    ) -> None:
        await self._bookings.update(booking=message.body)
