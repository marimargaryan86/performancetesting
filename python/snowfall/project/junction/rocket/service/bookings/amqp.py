from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib.transport.amqp import producer


class BookingProducer:
    def __init__(self, producer_obj: producer.Producer):
        self._producer = producer_obj

    async def publish(
        self,
        booking: models_pb2.Booking,
    ) -> None:
        await self._producer.publish(
            amqp_pb2.PlaceBookingTask(
                booking=booking,
            ),
            "bookings.prices",
        )


class BookingCancellationTaskProducer:
    def __init__(self, producer_obj: producer.Producer):
        self._producer = producer_obj

    async def publish(
        self,
        booking_cancellation: models_pb2.BookingCancellation,
    ) -> None:
        await self._producer.publish(
            amqp_pb2.HandleBookingCancellationTask(
                booking_cancellation=booking_cancellation,
            ),
            "bookings.cancellations",
        )
