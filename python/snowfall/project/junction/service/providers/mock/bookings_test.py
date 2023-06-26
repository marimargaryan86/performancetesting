import datetime

import pytest

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.service.orders.v1alpha import amqp_pb2
from snowfall.project.junction.go.service.orders.v1alpha import models_pb2 as orders_pb2
from snowfall.project.junction.service.providers.mock import bookings, cache
from snowfall.stdlib.format import protobuf

_UNKNOWN_ID = "bf624a85-205a-4717-b4e7-a83f6ec8ecb9"


def _generate_booking_task(price_quote_id: str) -> amqp_pb2.PlaceOrderTask:
    return amqp_pb2.PlaceOrderTask(
        booking=orders_pb2.Booking(
            trip_option=orders_pb2.TripOption(
                price_quote_id=price_quote_id,
            ),
        ),
    )


@pytest.fixture()
def place_order_task(price_quote: offers_pb2.PriceQuote) -> amqp_pb2.PlaceOrderTask:
    return _generate_booking_task(price_quote_id=price_quote.id)


@pytest.fixture()
async def booking(
    place_order_task: amqp_pb2.PlaceOrderTask,
    booker: bookings.Booker,
) -> orders_pb2.Booking:
    return await booker.book(place_order_task)


class TestBooker(object):
    async def test_unknown_price_quote_id_raises_error(
        self,
        booker: bookings.Booker,
    ) -> None:
        with pytest.raises(cache.PriceQuoteNotFoundError):
            await booker.book(_generate_booking_task(_UNKNOWN_ID))

    async def test_known_price_quote_id_returns_booking(
        self,
        price_quote_cache: cache.PriceQuoteCache,
        booker: bookings.Booker,
    ) -> None:
        price_quote_id = await price_quote_cache.store(
            cache.MockDetails(
                amount=1,
                currency="USD",
            ),
        )
        assert await booker.book(_generate_booking_task(price_quote_id)) is not None


class TestBookingModel(object):
    def test_is_confirmed(self, booking: orders_pb2.Booking) -> None:
        assert booking.status == orders_pb2.Booking.STATUS_CONFIRMED

    def test_has_provider_name(self, booking: orders_pb2.Booking) -> None:
        assert booking.provider_name

    def test_has_price(
        self,
        booking: orders_pb2.Booking,
        price_quote: offers_pb2.PriceQuote,
    ) -> None:
        assert (
            booking.provider_total_price.SerializeToString()
            == price_quote.price.SerializeToString()
        )


class TestTripBookingModel(object):
    def test_has_provider_booking_reference(self, booking: orders_pb2.Booking) -> None:
        assert booking.trip_result.provider_booking_reference

    def test_has_record_locator(self, booking: orders_pb2.Booking) -> None:
        assert booking.trip_result.record_locator

    def test_has_created_at(self, booking: orders_pb2.Booking) -> None:
        now = datetime.datetime.now(tz=datetime.UTC)
        recently = now - datetime.timedelta(minutes=1)
        created_at = protobuf.protobuf_to_datetime(booking.trip_result.created_at)
        assert created_at > recently
        assert created_at < now
