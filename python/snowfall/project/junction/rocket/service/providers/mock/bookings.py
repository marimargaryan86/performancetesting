import pathlib
import string as pystring
import uuid

from snowfall.project.junction.rocket.provider import bookings
from snowfall.project.junction.rocket.provider.v1alpha import bookings_pb2
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.project.junction.rocket.service.providers.mock import cache
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, producer, types


class Booker:
    def __init__(
        self,
        quote_cache: cache.QuoteCache,
        booking_storage: filesystem.Storage,
        provider_id: uuid.UUID,
        provider_name: str,
    ):
        self._quote_cache = quote_cache
        self._storage = booking_storage
        self._provider_id = str(provider_id)
        self._provider_name = provider_name

    async def book(
        self,
        task: amqp_pb2.PlaceBookingTask,
    ) -> models_pb2.Booking:
        price_quote = await self._quote_cache.fetch(
            task.booking.trip_option.price_quote_id,
        )
        if not price_quote:
            raise cache.QuoteNotFoundError()

        new_booking = task.booking

        new_booking.MergeFrom(
            models_pb2.Booking(
                status=models_pb2.Booking.STATUS_CONFIRMED,
                provider_id=self._provider_id,
                provider_name=self._provider_name,
                trip_option=models_pb2.TripOption(
                    price_quote_id=task.booking.trip_option.price_quote_id,
                    price=money.Money(
                        amount=price_quote.amount,
                        currency=money.Currency(price_quote.currency),
                    ).protobuf(),
                ),
                provider_booking=models_pb2.ProviderBooking(
                    booking_reference=string.uuid(),
                    record_locator=string.random(6, charset=pystring.ascii_uppercase),
                ),
            ),
        )
        await self._storage.put(
            pathlib.Path(new_booking.provider_booking.booking_reference),
            protobuf.AnySerializer[models_pb2.Booking].serialize(new_booking),
        )

        return new_booking


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
        message: types.Message[amqp_pb2.PlaceBookingTask],
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


class Transformer:
    def __init__(self) -> None:
        self._serializer = protobuf.AnySerializer[models_pb2.Booking]()

    async def raw_to_booking(self, raw: bytes) -> bookings_pb2.Booking:
        booking = self._serializer.deserialize(raw)
        return bookings_pb2.Booking(
            id=booking.provider_booking.booking_reference,
            status=bookings_pb2.Booking.STATUS_CONFIRMED,
            provider=bookings_pb2.Booking.Provider(
                id=booking.provider_id,
                name=booking.provider_name,
            ),
            trip=bookings_pb2.Booking.Trip(
                record_locator=booking.provider_booking.record_locator,
            ),
            prices=[
                bookings_pb2.Booking.Price(
                    type=bookings_pb2.Booking.Price.TYPE_TOTAL,
                    amount=booking.trip_option.price,
                ),
            ],
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )


class CancellationHandler:
    def __init__(
        self,
        booking_storage: filesystem.Storage,
        transformer: bookings.Transformer,
    ) -> None:
        self._storage = booking_storage
        self._transformer = transformer

    async def cancel(self, identifier: str) -> bookings_pb2.BookingCancellation:
        booking_raw = await self._storage.get(pathlib.Path(identifier))

        if not booking_raw:
            raise FileNotFoundError()

        booking = await self._transformer(booking_raw)
        price = next(
            price
            for price in booking.prices
            if price.type == bookings_pb2.Booking.Price.TYPE_TOTAL
        )

        price_amount = money.Money(
            amount=price.amount.units // 2,
            currency=money.Currency(price.amount.currency_code),
        )

        return bookings_pb2.BookingCancellation(
            provider_booking_reference=identifier,
            status=bookings_pb2.BookingCancellation.STATUS_REFUND_DUE,
            refunded_us=price_amount.protobuf(),
        )
