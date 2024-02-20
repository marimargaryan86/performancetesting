import datetime
import pathlib
import types
import uuid

from xsdata.formats.dataclass import parsers
from xsdata.formats.dataclass.parsers import config as parsers_config

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2, models_pb2
from snowfall.project.junction.provider.v1 import bookings_pb2
from snowfall.project.junction.service.providers.carnect import (
    adapter,
    cache,
    notifications,
)
from snowfall.stdlib import money, sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.carnect import client
from snowfall.vendor.carnect import config as carnect_settings
from snowfall.vendor.carnect.adapters import (
    cancel_reservation_adapter,
    reservation_adapter,
    veh_ret_res_adapter,
)
from snowfall.vendor.carnect.builders import (
    cancel_reservation_builder,
    reservation_builder,
    veh_ret_res_builder,
)
from snowfall.vendor.carnect.models import service

_DEFAULT_LANGUAGE = "en"
_STATUS_CONFIRMED = "Confirmed"

_STATUS_MAP = types.MappingProxyType({
    "Pending": bookings_pb2.Booking.STATUS_PENDING,
    "Confirmed": bookings_pb2.Booking.STATUS_CONFIRMED,
    "Failed": bookings_pb2.Booking.STATUS_ERROR,
    None: bookings_pb2.Booking.STATUS_ERROR,
})


def parse_reservation_output_from_raw(
    response: bytes,
) -> service.ServiceSoapGetVehReservationOutput:
    parser = parsers.XmlParser(
        config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
    )
    return parser.from_bytes(response, service.ServiceSoapGetVehReservationOutput)


class Transformer(object):
    def __init__(self, provider_identifier: uuid.UUID, provider_name: str):
        self._provider_id = str(provider_identifier)
        self._provider_name = provider_name

    async def raw_to_booking(self, raw: bytes) -> bookings_pb2.Booking:
        response = parse_reservation_output_from_raw(raw)
        res_adapter = reservation_adapter.ReservationAdapter(response)
        reservation = res_adapter.reservation()
        timestamp = res_adapter.get_timestamp()
        status = res_adapter.get_status()
        booking_status = _STATUS_MAP.get(status, bookings_pb2.Booking.STATUS_CANCELLED)

        try:
            vendor_reference = reservation.veh_segment_core.vendor.value  # type: ignore[union-attr]
        except AttributeError:
            vendor_reference = ""

        return bookings_pb2.Booking(
            id=str(res_adapter.get_id_context()),
            status=booking_status,
            provider=bookings_pb2.Booking.Provider(
                id=self._provider_id,
                name=self._provider_name,
            ),
            trip=bookings_pb2.Booking.Trip(
                record_locator=res_adapter.get_unique_id() or "",
                operator_booking_references=[vendor_reference],
            ),
            created_at=protobuf.datetime_to_protobuf(timestamp) if timestamp else None,
        )


class _CarnectCancellationError(Exception):
    """Raised when there is a Carnect-related issue."""


class BookingCancellationHandler(object):
    def __init__(
        self,
        carnect_client: client.CarnectClient,
        carnect_config: carnect_settings.Config,
    ) -> None:
        self._client = carnect_client
        self._carnect_config = carnect_config
        self._logger = stdout.get_logger()

    async def cancel_booking(
        self,
        provider_booking_reference: str,
    ) -> bookings_pb2.BookingCancellation:
        try:
            rs_adapter = await self._cancel_booking(provider_booking_reference)
        except (errors.HttpError, _CarnectCancellationError, ValueError):
            self._logger.exception(
                "Booking cancellation failed",
                provider_booking_reference=provider_booking_reference,
            )

            return bookings_pb2.BookingCancellation(
                provider_booking_reference=provider_booking_reference,
                status=bookings_pb2.BookingCancellation.STATUS_REFUND_FAILED,
            )

        try:
            amount = await self._get_refunded_us(rs_adapter, provider_booking_reference)
        except (adapter.FieldMissingError, _CarnectCancellationError):
            self._logger.exception(
                "Failed to get total amount",
                provider_booking_reference=provider_booking_reference,
            )
            return bookings_pb2.BookingCancellation(
                provider_booking_reference=provider_booking_reference,
                status=bookings_pb2.BookingCancellation.STATUS_REFUND_FAILED,
            )

        return bookings_pb2.BookingCancellation(
            provider_booking_reference=provider_booking_reference,
            status=bookings_pb2.BookingCancellation.STATUS_REFUND_DUE,
            refunded_us=amount.protobuf(),
        )

    async def _get_refunded_us(
        self,
        rs_adapter: cancel_reservation_adapter.CancelReservationAdapter,
        provider_booking_reference: str,
    ) -> money.Money:
        fees = adapter.get_optional_value(
            rs_adapter.cancel_info(),
            "veh_reservation.veh_segment_core.fees.fee",
            [],
        )
        if not fees:
            raise adapter.FieldMissingError(
                "Cancellation fee information is missing in cancellation response",
            )

        if fees[0].amount is None:
            raise adapter.FieldMissingError(
                "Cancellation fee amount is missing in cancellation response",
            )

        if fees[0].currency_code is None:
            raise adapter.FieldMissingError(
                "Cancellation fee currency_code is missing in cancellation response",
            )

        fee = money.from_string(
            string_amount=str(fees[0].amount),
            currency=money.Currency(fees[0].currency_code.upper()),
        )

        amount = money.Money(0, currency=fee.currency)
        if fee.amount == 0:
            amount = await self._get_total_amount(provider_booking_reference)

        return amount

    async def _get_total_amount(
        self,
        provider_booking_reference: str,
    ) -> money.Money:
        builder = veh_ret_res_builder.VehRetResRqBuilder(self._carnect_config)

        id_context, surname = sequence.from_composite_id(provider_booking_reference)
        builder.unique_id().id_context(id_context)
        builder.person_name().surname(surname)

        rs_adapter = veh_ret_res_adapter.VehRetResAdapter(
            await self._client.retrieve_reservation(builder),
        )
        if not rs_adapter.is_success():
            raise _CarnectCancellationError(rs_adapter.get_error())

        rs_core = rs_adapter.rs_core()
        amount = adapter.get_optional_value(
            rs_core,
            "veh_reservation.veh_segment_core.total_charge.estimated_total_amount",
            None,
        )
        currency_code = adapter.get_optional_value(
            rs_core,
            "veh_reservation.veh_segment_core.total_charge.currency_code",
            None,
        )

        if amount is None:
            raise adapter.FieldMissingError("missing value: total amount")
        if currency_code is None:
            raise adapter.FieldMissingError("missing value: currency code")

        return money.from_string(str(amount), money.Currency(currency_code.upper()))

    async def _cancel_booking(
        self,
        provider_booking_reference: str,
    ) -> cancel_reservation_adapter.CancelReservationAdapter:
        id_context, surname = sequence.from_composite_id(provider_booking_reference)

        cancel_rq_builder = cancel_reservation_builder.CancelReservationRqBuilder(
            self._carnect_config,
        )
        cancel_info_type = cancel_rq_builder.get_cancel_info_type()
        unique_id = cancel_info_type.add_unique_id()
        unique_id.id_context(id_context)
        cancel_info_type.get_person_name().surname(surname)

        response = await self._client.cancel_reservation(cancel_rq_builder)
        rs_adapter = cancel_reservation_adapter.CancelReservationAdapter(response)

        if not rs_adapter.is_success():
            raise _CarnectCancellationError(rs_adapter.get_error())

        return rs_adapter


class BookingHandler(object):
    def __init__(
        self,
        carnect_client: client.CarnectClient,
        carnect_config: carnect_settings.Config,
        booking_storage: filesystem.Storage,
        email_client: notifications.EmailClient,
    ):
        self._client = carnect_client
        self._email_client = email_client
        self._carnect_config = carnect_config
        self._logger = stdout.get_logger()
        self._storage = booking_storage

    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
        price_quote: cache.PriceQuote,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            res_adapter, raw_data = await self._make_booking(
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

        id_context = res_adapter.get_id_context()
        reservation = res_adapter.reservation()
        if not reservation or not id_context or not res_adapter.is_success():
            self._logger.error(
                "Failed to create booking",
                offer_id=price_quote.quote_id,
                booking_id=task.booking.id,
                error=res_adapter.get_error(),
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = raw_data.decode()

            return new_booking

        if res_adapter.get_status() == _STATUS_CONFIRMED:
            template = notifications.BookingNotification(task.metadata, res_adapter)
            try:
                await self._email_client.send_email_html_template(
                    mail_to=task.contact_details.email,
                    subject=template.subject,
                    body=template.body,
                )
            except notifications.EmailNotificationError:
                self._logger.exception("Failed to send booking notification")

        provider_booking_reference = sequence.to_composite_id([
            id_context,
            task.passengers[0].last_name,
        ])

        try:
            booking = self._res_adapter_to_booking(
                provider_booking_reference=provider_booking_reference,
                unique_id=res_adapter.get_unique_id(),
                reservation=reservation,
                raw_data=raw_data,
            )
        except adapter.FieldMissingError:
            self._logger.exception(
                "Failed to create booking",
                offer_id=price_quote.quote_id,
                booking_id=task.booking.id,
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = raw_data.decode()

            return new_booking

        new_booking.MergeFrom(booking)

        await self._storage.put(
            pathlib.Path(provider_booking_reference),
            raw_data,
        )

        return new_booking

    async def _make_booking(
        self,
        task: amqp_pb2.PlaceOrderTask,
        price_quote: cache.PriceQuote,
    ) -> tuple[reservation_adapter.ReservationAdapter, bytes]:
        request_builder = self._create_request_builder(task, price_quote.quote_id)

        response, raw_data = await self._client.reservation(request_builder)
        res_adapter = reservation_adapter.ReservationAdapter(response)

        return res_adapter, raw_data

    def _res_adapter_to_booking(
        self,
        provider_booking_reference: str,
        unique_id: str | None,
        reservation: service.VehicleReservationType,
        raw_data: bytes,
    ) -> models_pb2.Booking:
        return models_pb2.Booking(
            status=models_pb2.Booking.STATUS_CONFIRMED,
            provider_total_price=get_total_price(reservation).protobuf(),
            trip_result=models_pb2.TripBooking(
                provider_booking_reference=provider_booking_reference,
                record_locator=unique_id if unique_id else "",
                created_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC),
                ),
            ),
            raw_data=raw_data.decode(),
        )

    def _create_request_builder(
        self,
        task: amqp_pb2.PlaceOrderTask,
        offer_id_context: str,
    ) -> reservation_builder.ReservationBuilder:
        res_rq = reservation_builder.ReservationBuilder(config=self._carnect_config)
        res_rq.veh_pref_code(offer_id_context)

        driver = task.passengers[0]
        driver_rq = res_rq.primary_driver()
        driver_rq.surname(driver.last_name)
        driver_rq.given_name(driver.first_name)
        driver_rq.email(task.contact_details.email)
        driver_rq.birth_date(
            protobuf.protobuf_to_date(driver.date_of_birth),
        )
        driver_rq.language(_DEFAULT_LANGUAGE)
        driver_rq.add_phone(task.contact_details.phone.e164_number)
        driver_rq.citizen_country_code(driver.doc_details.issue_county)
        driver_addr = driver_rq.add_address()
        address = ", ".join(task.contact_details.address.address_lines)
        driver_addr.street_nmbr(_remove_special_characters(address))
        driver_addr.city_name(
            _remove_special_characters(task.contact_details.address.locality),
        )
        driver_addr.postal_code(
            _remove_special_characters(task.contact_details.address.postal_code),
        )
        return res_rq


def _remove_special_characters(string: str) -> str:
    """Remove special characters from string, because of Carnect limitation.

    Ref: https://doc.carnect.com/ota2007/endpoints.html#id16.
    """
    chars_list = "!”§$%&/()=?`;:_>"
    for char in chars_list:
        string = string.replace(char, " ")
    return string


def get_total_price(  # noqa: WPS238
    reservation: service.VehicleReservationType,
) -> money.Money:
    try:
        amount = reservation.veh_segment_core.total_charge.estimated_total_amount  # type: ignore[union-attr]
    except AttributeError as error:
        raise adapter.FieldMissingError() from error

    try:
        currency_code = reservation.veh_segment_core.total_charge.currency_code  # type: ignore[union-attr]
    except AttributeError as exc:
        raise adapter.FieldMissingError() from exc

    if not amount:
        raise adapter.FieldMissingError(
            "Price amount field is missing: {0}".format(amount),
        )
    if not currency_code:
        raise adapter.FieldMissingError(
            "Price currency_code field is missing: {0}".format(currency_code),
        )

    return money.from_string(
        str(amount),
        currency=money.Currency(currency_code.upper()),
    )
