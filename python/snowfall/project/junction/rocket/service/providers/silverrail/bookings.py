import uuid

from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.project.junction.rocket.service.providers.silverrail import cache
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.vendor.silverrail import client


class Booker:
    def __init__(
        self,
        quote_cache: cache.QuoteCache,
        booking_storage: filesystem.Storage,
        silverrail_client: client.SilverrailClient,
        provider_id: uuid.UUID,
        provider_name: str,
    ):
        self._quote_cache = quote_cache
        self._storage = booking_storage
        self._client = silverrail_client
        self._provider_id = str(provider_id)
        self._provider_name = provider_name
        self._logger = stdout.get_logger()

    async def book(self, task: amqp_pb2.PlaceBookingTask) -> models_pb2.Booking:
        return models_pb2.Booking()


class Consumer:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.PlaceBookingTask],
        producer_obj: producer.Producer,
        booker: Booker,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._booker = booker

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: amqp_types.Message[amqp_pb2.PlaceBookingTask],
    ) -> None:
        try:
            booking_result = await self._booker.book(message.body)
        except cache.QuoteNotFoundError:
            return

        await self._producer.publish(
            booking_result,
            routing_key="bookings.results.prices",
        )

        await message.ack()
