import datetime
import pathlib
import string as pystring
import uuid

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2, models_pb2
from snowfall.project.junction.provider.v1alpha import bookings_pb2
from snowfall.project.junction.service.providers.mock import cache
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, producer, types


class Booker(object):
    def __init__(
        self,
        price_quote_cache: cache.PriceQuoteCache,
        booking_storage: filesystem.Storage,
        provider_id: uuid.UUID,
        provider_name: str,
    ):
        self._cache = price_quote_cache
        self._storage = booking_storage
        self._provider_id = str(provider_id)
        self._provider_name = provider_name

    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
    ) -> models_pb2.Booking:
        price_quote = await self._cache.fetch(task.booking.trip_option.price_quote_id)

        if not price_quote:
            raise cache.PriceQuoteNotFoundError()

        new_booking = task.booking

        new_booking.MergeFrom(
            models_pb2.Booking(
                status=models_pb2.Booking.STATUS_CONFIRMED,
                provider_id=self._provider_id,
                provider_name=self._provider_name,
                provider_total_price=money.Money(
                    amount=price_quote.amount,
                    currency=money.Currency(price_quote.currency),
                ).protobuf(),
                trip_result=models_pb2.TripBooking(
                    provider_booking_reference=string.uuid(),
                    record_locator=string.random(6, charset=pystring.ascii_uppercase),
                    created_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.now(tz=datetime.UTC),
                    ),
                ),
            ),
        )
        await self._storage.put(
            pathlib.Path(new_booking.trip_result.provider_booking_reference),
            protobuf.AnySerializer[models_pb2.Booking].serialize(new_booking),
        )

        return new_booking


class Consumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.PlaceOrderTask],
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
        message: types.Message[amqp_pb2.PlaceOrderTask],
    ) -> None:
        try:
            booking_result = await self._booker.book(message.body)
        except cache.PriceQuoteNotFoundError:
            return

        await self._producer.publish(
            booking_result,
            routing_key="orders.result.offer",
        )

        await message.ack()


class Transformer(object):
    def __init__(self) -> None:
        self._serializer = protobuf.AnySerializer[models_pb2.Booking]()

    async def raw_to_booking(self, raw: bytes) -> bookings_pb2.Booking:
        booking = self._serializer.deserialize(raw)
        return bookings_pb2.Booking(
            id=booking.trip_result.provider_booking_reference,
            status=bookings_pb2.Booking.STATUS_CONFIRMED,
            provider=bookings_pb2.Booking.Provider(
                id=booking.provider_id,
                name=booking.provider_name,
            ),
            trip=bookings_pb2.Booking.Trip(
                record_locator=booking.trip_result.record_locator,
            ),
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )
