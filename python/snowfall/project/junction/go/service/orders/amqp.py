from snowfall.project.junction.go.service.orders.v1 import amqp_pb2, models_pb2
from snowfall.stdlib.transport.amqp import producer


class OrderProducer:
    def __init__(self, producer_obj: producer.Producer):
        self._producer = producer_obj

    async def publish(
        self,
        journey: models_pb2.Journey,
        order: models_pb2.Order,
        reseller_id: str,
    ) -> None:
        for booking in order.bookings:
            await self._producer.publish(
                amqp_pb2.PlaceOrderTask(
                    booking=booking,
                    contact_details=journey.contact_details,
                    passengers=order.passengers,
                    residence_address=order.residence_address,
                    metadata=amqp_pb2.OrderMetadata(
                        journey_id=order.journey_id,
                        order_id=order.id,
                        booking_id=booking.id,
                        passenger_name_record=journey.passenger_name_record,
                    ),
                    reseller_id=reseller_id,
                ),
                "orders.offers",
            )
