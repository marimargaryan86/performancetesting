import datetime

import structlog

from snowfall.project.junction.go.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.provider import notifications as base_notifications
from snowfall.project.junction.service.providers.karhoo import cache, notifications
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.vendor.karhoo import client
from snowfall.vendor.karhoo.models import bookings, passenger


class BookingHandler(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 15

    def __init__(
        self,
        karhoo_client: client.KarhooClient,
        notifier: base_notifications.Notifier,
    ):
        self._client = karhoo_client
        self._logger = structlog.get_logger(__name__)
        self._notifier = notifier

    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        booking_response = await self._make_booking(task=task, details=details)

        new_booking.MergeFrom(
            models_pb2.Booking(
                status=models_pb2.Booking.STATUS_CONFIRMED,
                provider_total_price=money.from_string(
                    string_amount=str(
                        booking_response.fare.total,
                    ),
                    currency=money.Currency(booking_response.fare.currency),
                ).protobuf(),
                trip_result=models_pb2.TripBooking(
                    provider_booking_reference=str(booking_response.id),
                    record_locator=(
                        booking_response.follow_code
                        if booking_response.follow_code
                        else ""
                    ),
                    created_at=protobuf.datetime_to_protobuf(
                        (
                            datetime.datetime.strptime(
                                booking_response.date_booked,
                                "%Y-%m-%dT%H:%M",
                            ).replace(
                                tzinfo=datetime.UTC,
                            )
                            if booking_response.date_booked
                            else datetime.datetime.now(tz=datetime.UTC)
                        ),
                    ),
                ),
                raw_data=booking_response.json(),
            ),
        )

        return new_booking

    async def _make_booking(
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> bookings.BookingResponse:
        booking = bookings.Booking(
            quote_id=details.quote_id,
            passengers=passenger.Passengers(
                additional_passengers=len(task.passengers) - 1,
                passenger_details=[
                    passenger.PassengerDetails(
                        first_name=passenger_details.first_name,
                        last_name=passenger_details.last_name,
                        email=task.contact_details.email,
                        phone_number=str(task.contact_details.phone),
                        locale=None,
                    )
                    for passenger_details in task.passengers
                ],
                # TODO: this should not be hardcoded forever
                luggage=passenger.Luggage(
                    total=len(task.passengers),
                ),
                # TODO: currently ignoring these fields
                meta=None,
                partner_trip_id=None,
                flight_number=None,
                train_number=None,
                cost_center_reference=None,
                comments=None,
                train_time=None,
            ),
        )
        booking_result = await self._client.book_trip(booking)
        if booking_result.status == "CONFIRMED":
            try:
                # TODO: this should be handled in a separate service
                await self._notifier.send(
                    notifications.BookingNotification(task.metadata, booking_result),
                )
            except base_notifications.NotificationError:
                self._logger.exception()

        return booking_result
