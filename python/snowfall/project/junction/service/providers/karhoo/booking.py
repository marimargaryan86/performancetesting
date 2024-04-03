import datetime
import pathlib

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2, models_pb2
from snowfall.project.junction.provider import notifications as base_notifications
from snowfall.project.junction.service.providers.karhoo import cache, notifications
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.karhoo import client
from snowfall.vendor.karhoo.models import bookings, passenger


class BookingHandler:
    _poll_retries_limit = 10
    _wait_time_between_polling = 15

    def __init__(
        self,
        karhoo_client: client.KarhooClient,
        notifier: base_notifications.Notifier,
        booking_storage: filesystem.Storage,
    ):
        self._client = karhoo_client
        self._logger = stdout.get_logger()
        self._notifier = notifier
        self._storage = booking_storage

    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
        price_quote: cache.PriceQuote,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            booking_response = await self._make_booking(
                task=task,
                price_quote=price_quote,
            )
        except errors.HttpError as ex:
            self._logger.exception(
                "Failed to create booking",
                offer_id=price_quote.quote_id,
                booking_id=task.booking.id,
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = repr(ex)

            return new_booking

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
                                "%Y-%m-%dT%H:%M:%SZ",
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

        await self._storage.put(
            pathlib.Path(booking_response.id),
            booking_response.json().encode(),
        )

        return new_booking

    async def _make_booking(
        self,
        task: amqp_pb2.PlaceOrderTask,
        price_quote: cache.PriceQuote,
    ) -> bookings.BookingResponse:
        booking = bookings.Booking(
            quote_id=price_quote.quote_id,
            passengers=passenger.Passengers(
                additional_passengers=len(task.passengers) - 1,
                passenger_details=[
                    passenger.PassengerDetails(
                        first_name=passenger_details.first_name,
                        last_name=passenger_details.last_name,
                        email=task.contact_details.email,
                        phone_number=task.contact_details.phone.e164_number,
                        locale=None,
                    )
                    for passenger_details in task.passengers
                ],
                # TODO(reuben.t): this should not be hardcoded forever
                luggage=passenger.Luggage(
                    total=len(task.passengers),
                ),
            ),
        )

        booking_result = await self._client.book_trip(booking)

        if booking_result.status == "CONFIRMED":
            try:
                # TODO(reuben.t): this should be handled in a separate service
                await self._notifier.send(
                    notifications.BookingNotification(task.metadata, booking_result),
                )
            except base_notifications.NotificationError:
                self._logger.exception("A notification error occurred.")

        return booking_result
