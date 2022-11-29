import structlog

from snowfall.project.junction.service.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.service.providers.ask2go import booking, cache
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types

_PROVIDER_NAME = "Ask2Go"


class OrderConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[orders_amqp_pb2.PlaceOrderTask],
        producer_obj: producer.Producer,
        booking_handler: booking.BookingHandler,
        offer_cache: cache.OfferCache,
    ):
        self._booking = booking_handler
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[orders_amqp_pb2.PlaceOrderTask],
    ) -> None:
        offer_details = await self._cache.fetch(
            amqp_message.body.booking.trip_option.id,
        )
        amqp_message.body.booking.provider_name = _PROVIDER_NAME

        if not offer_details:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=amqp_message.body.booking.id,
                key=amqp_message.body.booking.trip_option.id,
            )

            return

        await self._producer.publish(
            await self._booking.book(task=amqp_message.body, details=offer_details),
            routing_key="orders.result.offer",
        )
