import asyncio
import datetime
import pathlib
import types
import uuid
from collections.abc import Sequence

import more_itertools
import orjson
import phonenumbers
import prometheus_client
import pycountry

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2, models_pb2
from snowfall.project.junction.provider import notifications as base_notifications
from snowfall.project.junction.provider.v1 import bookings_pb2
from snowfall.project.junction.service.providers.ask2go import (
    cache,
    criteria,
    models,
    notifications,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.ask2go import client, errors
from snowfall.vendor.ask2go.models import booking, common

_PROVIDER_STATUS_MAPPING = types.MappingProxyType(
    {
        "BookingUpdated": bookings_pb2.Booking.STATUS_UNSPECIFIED,
        "PricingSuccedded": bookings_pb2.Booking.STATUS_UNSPECIFIED,
        "PricingPending": bookings_pb2.Booking.STATUS_UNSPECIFIED,
        "ValidationPending": bookings_pb2.Booking.STATUS_UNSPECIFIED,
        "ValidationDone": bookings_pb2.Booking.STATUS_UNSPECIFIED,
        "ScheduleChange": bookings_pb2.Booking.STATUS_UNSPECIFIED,
        "BookingPending": bookings_pb2.Booking.STATUS_PENDING,
        "Completed": bookings_pb2.Booking.STATUS_CONFIRMED,
        "BookingDone (if related to hotel)": bookings_pb2.Booking.STATUS_CONFIRMED,
        "PNRCreated": bookings_pb2.Booking.STATUS_NOT_TICKETED,
        "BookingDone (if related to air)": bookings_pb2.Booking.STATUS_NOT_TICKETED,
        "Unknown": bookings_pb2.Booking.STATUS_ERROR,
        "DBError": bookings_pb2.Booking.STATUS_ERROR,
        "Expired": bookings_pb2.Booking.STATUS_ERROR,
        "BookingFailed": bookings_pb2.Booking.STATUS_ERROR,
        "PricingFailed": bookings_pb2.Booking.STATUS_ERROR,
        "PriceDifference": bookings_pb2.Booking.STATUS_ERROR,
        "Duplicate": bookings_pb2.Booking.STATUS_ERROR,
        "Timeout": bookings_pb2.Booking.STATUS_ERROR,
        "TicketingFailed": bookings_pb2.Booking.STATUS_ERROR,
        "TicketingSkipped": bookings_pb2.Booking.STATUS_ERROR,
        "Fraud": bookings_pb2.Booking.STATUS_ERROR,
        "NotFound": bookings_pb2.Booking.STATUS_ERROR,
        "GeneralException": bookings_pb2.Booking.STATUS_ERROR,
        "Cancelled": bookings_pb2.Booking.STATUS_CANCELLED,
    },
)


class BookingError(errors.Ask2GoError):
    def __init__(
        self,
        message: str,
        *,
        status: str,
        details: Sequence[booking.InformationError] | None,
    ):
        super().__init__(message)
        self.status = status
        self.details = details


class BookingHandler(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 1
    _counter_bookings = prometheus_client.Counter(
        "ask2go_bookings_total",
        "Total number of bookings placed.",
        labelnames=("status",),
    )

    def __init__(
        self,
        ask2go_client: client.Ask2GoClient,
        notifier: base_notifications.Notifier,
        booking_storage: filesystem.Storage,
        *,
        override_double_booking_check: bool,
    ):
        self._client = ask2go_client
        self._logger = stdout.get_logger()
        self._notifier = notifier
        self._storage = booking_storage
        self._override_double_booking_check = override_double_booking_check

    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
        quote: cache.PriceQuote,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            booking_result = await self._make_booking(
                contact_details=task.contact_details,
                passengers=task.passengers,
                quote=quote,
                metadata=task.metadata,
            )
        except (errors.Ask2GoError, phonenumbers.NumberParseException) as error:
            if isinstance(error, errors.Ask2GoError):
                await self._log_exception(error)

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = repr(error)

            return new_booking

        new_booking.MergeFrom(
            models_pb2.Booking(
                status=models_pb2.Booking.STATUS_NOT_TICKETED,
                provider_total_price=money.from_string(
                    string_amount=str(
                        booking_result.price_information["bookPrice"]["price"],
                    ),
                    currency=money.Currency(
                        booking_result.price_information["bookPrice"]["currency"],
                    ),
                ).protobuf(),
                trip_result=models_pb2.TripBooking(
                    provider_booking_reference=str(
                        booking_result.information.booking_id,
                    ),
                    record_locator=more_itertools.first(
                        booking_result.information.record_locators or [""],
                    ),
                    operator_booking_references=booking_result.information.check_in_locators,
                    created_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.now(tz=datetime.UTC),
                    ),
                ),
                raw_data=booking_result.model_dump_json(),
            ),
        )

        return new_booking

    async def _log_exception(self, error: errors.Ask2GoError) -> None:
        if isinstance(error, BookingError):
            self._logger.exception(
                "Booking failed",
                status=error.status,
                details=[
                    {"code": detail.code, "message": detail.message}
                    for detail in error.details or []
                ],
            )
        elif isinstance(error, errors.RequestError):
            self._logger.exception(
                "Booking failed",
                method=error.request.method,
                url=error.request.url,
                request=error.request.body,
            )
        elif isinstance(error, errors.HttpStatusError):
            self._logger.exception(
                "Booking failed",
                method=error.request.method,
                url=error.request.url,
                request=error.request.body,
                status_code=error.response.status_code,
                response=error.response.body,
            )
        else:
            self._logger.exception()

    async def _make_booking(
        self,
        contact_details: models_pb2.ContactDetails,
        passengers: Sequence[models_pb2.Passenger],
        quote: cache.PriceQuote,
        metadata: amqp_pb2.OrderMetadata,
    ) -> booking.Booking:
        number = phonenumbers.parse(contact_details.phone.e164_number)
        country = pycountry.countries.get(
            alpha_2=contact_details.address.region_code,
        )

        booking_result = await self._client.create_booking(
            pricing_id=quote.pricing_id,
            transaction_id=quote.transaction_id,
            passengers=[
                common.Passenger(
                    first_name=passenger.first_name,
                    last_name=passenger.last_name,
                    name_title=models_pb2.Passenger.Title.Name(
                        passenger.title,
                    )[6:].capitalize(),
                    gender=models.gender_from_proto(passenger.gender),
                    type=criteria.get_passenger_type(
                        protobuf.protobuf_to_date(passenger.date_of_birth),
                        datetime.datetime.now(
                            tz=datetime.UTC,
                        ).date(),  # TODO: date of travel
                    ),
                    birth_date=protobuf.protobuf_to_date(passenger.date_of_birth),
                    traveler_document=models.traveler_document_from_proto(
                        passenger.doc_details,
                    ),
                )
                for passenger in passengers
            ],
            contact=common.Contact(
                address="\n".join(contact_details.address.address_lines),
                city=contact_details.address.locality,
                postal_code=contact_details.address.postal_code,
                country=common.Country(
                    code=country.alpha_2,
                    name=country.name,
                ),
                phone=common.Phone(
                    country_code=str(number.country_code),
                    number=str(number.national_number),
                ),
                email=contact_details.email,
            ),
        )
        self._validate_booking_is_pending(booking_result)

        await self._client.update_booking_billing_address(
            booking_ref_id=booking_result.id,
            transaction_id=booking_result.transaction_id,
            override_double_booking_check=self._override_double_booking_check,
        )
        booking_result, raw_response = await self._poll_booking(booking_result)
        self._validate_booking_is_done(booking_result)
        await self._storage.put(pathlib.Path(booking_result.id), raw_response)

        try:
            # TODO: this should be handled in a separate service
            await self._notifier.send(
                notifications.BookingNotification(metadata, booking_result),
            )
        except base_notifications.NotificationError:
            self._logger.exception()

        return booking_result

    async def _poll_booking(
        self,
        booking_result: booking.Booking,
    ) -> tuple[booking.Booking, bytes]:
        for _ in range(self._poll_retries_limit):
            booking_result, raw_response = await self._client.get_booking(
                booking_ref_id=booking_result.id,
                transaction_id=booking_result.transaction_id,
            )

            if booking_result.contact_details:
                return booking_result, raw_response

            await asyncio.sleep(self._wait_time_between_polling)

        raise BookingError(
            "Booking did not complete in time",
            status=booking_result.information.status,
            details=booking_result.information.errors,
        )

    def _validate_booking_is_pending(self, booking_result: booking.Booking) -> None:
        status = booking_result.information.status

        if status not in {"BookingDone", "BookingPending"}:
            self._counter_bookings.labels(status=status).inc()
            raise BookingError(
                "Booking failed",
                status=booking_result.information.status,
                details=booking_result.information.errors,
            )

    def _validate_booking_is_done(self, booking_result: booking.Booking) -> None:
        self._counter_bookings.labels(status=booking_result.information.status).inc()

        if booking_result.information.status != "BookingDone":
            raise BookingError(
                "Booking failed",
                status=booking_result.information.status,
                details=booking_result.information.errors,
            )


class Transformer(object):
    def __init__(self, provider_identifier: uuid.UUID, provider_name: str):
        self._provider_id = str(provider_identifier)
        self._provider_name = provider_name

    async def raw_to_booking(self, raw: bytes) -> bookings_pb2.Booking:
        booking_result = booking.Booking(**orjson.loads(raw))

        return bookings_pb2.Booking(
            id=str(booking_result.information.booking_id),
            status=_PROVIDER_STATUS_MAPPING.get(
                booking_result.information.status,
                bookings_pb2.Booking.STATUS_UNSPECIFIED,
            ),
            provider=bookings_pb2.Booking.Provider(
                id=self._provider_id,
                name=self._provider_name,
            ),
            trip=bookings_pb2.Booking.Trip(
                record_locator=more_itertools.first(
                    booking_result.information.record_locators or [""],
                ),
                operator_booking_references=booking_result.information.check_in_locators,
            ),
            # TODO: No idea how to get created_at or updated_at from the booking model.
        )
