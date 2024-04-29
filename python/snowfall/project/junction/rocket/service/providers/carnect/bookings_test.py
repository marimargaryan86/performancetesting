from unittest import mock

from snowfall.project.junction.rocket.provider.v1alpha import bookings_pb2
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.project.junction.rocket.service.providers.carnect import bookings
from snowfall.stdlib.transport.amqp import types


async def test_consume_process_message_successful(  # noqa: WPS218
    booking_task_mock: types.Message[amqp_pb2.PlaceBookingTask],
    booking_consumer_mock: bookings.Consumer,
) -> None:
    producer = booking_consumer_mock._producer  # noqa: SLF001
    producer.publish = mock.AsyncMock()  # type: ignore[method-assign]
    await booking_consumer_mock._process_message(booking_task_mock)  # noqa: SLF001
    producer.publish.assert_awaited_once()

    assert producer.publish.call_args[1]["routing_key"] == "bookings.results.prices"

    booking: models_pb2.Booking = producer.publish.call_args[0][0]

    assert booking.reseller_id == booking_task_mock.body.booking.reseller_id
    assert booking.provider_id == booking_task_mock.body.booking.provider_id
    assert booking.status == booking_task_mock.body.booking.status
    assert (
        booking.trip_option.price_quote_id
        == booking_task_mock.body.booking.trip_option.price_quote_id
    )
    assert (
        booking.trip_option.price.currency_code
        == booking_task_mock.body.booking.trip_option.price.currency_code  # noqa: WPS219
    )
    assert (
        booking.trip_option.price.units
        == booking_task_mock.body.booking.trip_option.price.units  # noqa: WPS219
    )
    assert (
        booking.provider_booking.record_locator
        == booking_task_mock.body.booking.provider_booking.record_locator
    )
    assert booking.provider_booking.booking_reference == "VEVTNzU1NjAxNDQxMzc0AExhc3QA"
    assert booking.provider_booking.raw_data is not None


async def test_booking_cancellation_successful(
    cancellation_handler_mock: bookings.CancellationHandler,
) -> None:
    booking_reference = "VEVTNzU4MTQxMDcwNDQwAFRlc3QA"

    cancellation = await cancellation_handler_mock.cancel(identifier=booking_reference)

    assert cancellation.status == bookings_pb2.BookingCancellation.STATUS_REFUND_DUE
    assert cancellation.provider_booking_reference == booking_reference
    assert cancellation.refunded_us.units == 62
    assert cancellation.refunded_us.currency_code == "EUR"
