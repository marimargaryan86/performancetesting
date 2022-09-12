from snowfall.project.junction.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.stdlib.transport import amqp


class OrderProducer(object):
    def __init__(self, producer: amqp.Producer):
        self._producer = producer

    async def publish(
        self,
        journey: models_pb2.Journey,
        order: models_pb2.Order,
    ) -> None:
        for booking in order.bookings:
            await self._producer.publish(
                amqp_pb2.PlaceOrderTask(
                    booking=booking,
                    contact_details=journey.contact_details,
                    passengers=order.passengers,
                    metadata=amqp_pb2.OrderMetadata(
                        journey_id=order.journey_id,
                        order_id=order.id,
                        booking_id=booking.id,
                        passenger_name_record=journey.passenger_name_record,
                    ),
                ),
                "orders.offers",
            )
