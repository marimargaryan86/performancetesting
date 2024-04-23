import pathlib
import types
import uuid

import httpx
from xsdata.formats.dataclass import parsers
from xsdata.formats.dataclass.parsers import config as parsers_config

from snowfall.project.junction.rocket.provider.v1alpha import bookings_pb2
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.project.junction.rocket.service.providers.carnect import (
    cache,
    errors,
)
from snowfall.project.junction.rocket.service.providers.carnect.searches import (
    get_optional_value,
)
from snowfall.stdlib import money, sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types
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

_STATUS_CONFIRMED = "Confirmed"
_DEFAULT_LANGUAGE = "en"


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
        raise errors.FieldMissingError() from error

    try:
        currency_code = reservation.veh_segment_core.total_charge.currency_code  # type: ignore[union-attr]
    except AttributeError as exc:
        raise errors.FieldMissingError() from exc

    if not amount:
        raise errors.FieldMissingError(
            "Price amount field is missing: {0}".format(amount),
        )
    if not currency_code:
        raise errors.FieldMissingError(
            "Price currency_code field is missing: {0}".format(currency_code),
        )

    return money.from_string(
        str(amount),
        currency=money.Currency(currency_code.upper()),
    )


class Booker:
    def __init__(
        self,
        quote_cache: cache.QuoteCache,
        booking_storage: filesystem.Storage,
        carnect_client: client.CarnectClient,
        carnect_config: carnect_settings.Config,
        provider_id: uuid.UUID,
        provider_name: str,
    ):
        self._quote_cache = quote_cache
        self._storage = booking_storage
        self._client = carnect_client
        self._carnect_config = carnect_config
        self._provider_id = str(provider_id)
        self._provider_name = provider_name
        self._logger = stdout.get_logger()

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

        try:
            res_adapter, raw_data = await self._make_booking(
                task=task,
                price_quote=price_quote,
            )
        except httpx.HTTPError as ex:
            self._logger.exception(
                "Failed to create booking",
                offer_id=price_quote.quote_id,
                booking_id=task.booking.id,
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.provider_booking.raw_data = repr(ex)

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
            new_booking.provider_booking.raw_data = raw_data.decode()

            return new_booking

        provider_booking_reference = sequence.to_composite_id([
            id_context,
            task.booking.passengers[0].last_name,
        ])

        try:
            booking = self._res_adapter_to_booking(
                price_quote_id=price_quote.quote_id,
                provider_booking_reference=provider_booking_reference,
                unique_id=res_adapter.get_unique_id(),
                reservation=reservation,
                raw_data=raw_data,
            )
        except errors.FieldMissingError:
            self._logger.exception(
                "Failed to create booking",
                offer_id=price_quote.quote_id,
                booking_id=task.booking.id,
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.provider_booking.raw_data = raw_data.decode()

            return new_booking

        new_booking.MergeFrom(booking)

        await self._storage.put(
            pathlib.Path(new_booking.provider_booking.booking_reference),
            protobuf.AnySerializer[models_pb2.Booking].serialize(new_booking),
        )

        return new_booking

    async def _make_booking(
        self,
        task: amqp_pb2.PlaceBookingTask,
        price_quote: cache.PriceQuote,
    ) -> tuple[reservation_adapter.ReservationAdapter, bytes]:
        request_builder = self._create_request_builder(task, price_quote.quote_id)

        response, raw_data = await self._client.reservation(request_builder)
        res_adapter = reservation_adapter.ReservationAdapter(response)

        return res_adapter, raw_data

    def _res_adapter_to_booking(
        self,
        price_quote_id: str,
        provider_booking_reference: str,
        unique_id: str | None,
        reservation: service.VehicleReservationType,
        raw_data: bytes,
    ) -> models_pb2.Booking:
        return models_pb2.Booking(
            status=models_pb2.Booking.STATUS_CONFIRMED,
            provider_id=self._provider_id,
            provider_name=self._provider_name,
            trip_option=models_pb2.TripOption(
                price_quote_id=price_quote_id,
                price=get_total_price(reservation).protobuf(),
            ),
            provider_booking=models_pb2.ProviderBooking(
                record_locator=unique_id or "",
                booking_reference=provider_booking_reference,
                raw_data=raw_data.decode(),
            ),
        )

    def _create_request_builder(
        self,
        task: amqp_pb2.PlaceBookingTask,
        offer_id_context: str,
    ) -> reservation_builder.ReservationBuilder:
        res_rq = reservation_builder.ReservationBuilder(config=self._carnect_config)
        res_rq.veh_pref_code(offer_id_context)

        driver = task.booking.passengers[0]
        driver_rq = res_rq.primary_driver()
        driver_rq.surname(driver.last_name)
        driver_rq.given_name(driver.first_name)
        driver_rq.email(driver.contact_details.email)
        driver_rq.birth_date(
            protobuf.protobuf_to_date(driver.date_of_birth),
        )
        driver_rq.language(_DEFAULT_LANGUAGE)
        driver_rq.add_phone(driver.contact_details.phone.e164_number)
        driver_rq.citizen_country_code(driver.doc_details.issue_county)
        driver_addr = driver_rq.add_address()
        address = ", ".join(driver.contact_details.address.address_lines)
        driver_addr.street_nmbr(_remove_special_characters(address))
        driver_addr.city_name(
            _remove_special_characters(driver.contact_details.address.locality),
        )
        driver_addr.postal_code(
            _remove_special_characters(driver.contact_details.address.postal_code),
        )
        return res_rq


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


class Transformer:
    _status_map = types.MappingProxyType({
        "Pending": bookings_pb2.Booking.STATUS_PENDING,
        "Confirmed": bookings_pb2.Booking.STATUS_CONFIRMED,
        "Failed": bookings_pb2.Booking.STATUS_ERROR,
        None: bookings_pb2.Booking.STATUS_ERROR,
    })

    def __init__(self) -> None:
        self._serializer = protobuf.AnySerializer[models_pb2.Booking]()

    async def raw_to_booking(self, raw: bytes) -> bookings_pb2.Booking:
        booking = self._serializer.deserialize(raw)
        raw_data = booking.provider_booking.raw_data

        response = self._parse_reservation_output_from_raw(raw_data)
        res_adapter = reservation_adapter.ReservationAdapter(response)
        reservation = res_adapter.reservation()
        status = res_adapter.get_status()
        booking_status = self._status_map.get(
            status,
            bookings_pb2.Booking.STATUS_CANCELLED,
        )

        try:
            vendor_reference = reservation.veh_segment_core.vendor.value  # type: ignore[union-attr]
        except AttributeError:
            vendor_reference = ""

        return bookings_pb2.Booking(
            id=booking.provider_booking.booking_reference,
            status=booking_status,
            provider=bookings_pb2.Booking.Provider(
                id=booking.provider_id,
                name=booking.provider_name,
            ),
            trip=bookings_pb2.Booking.Trip(
                record_locator=res_adapter.get_unique_id() or "",
                operator_booking_references=[vendor_reference],
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

    def _parse_reservation_output_from_raw(
        self,
        response: str,
    ) -> service.ServiceSoapGetVehReservationOutput:
        parser = parsers.XmlParser(
            config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
        )
        return parser.from_string(response, service.ServiceSoapGetVehReservationOutput)


class CancellationHandler:
    def __init__(
        self,
        carnect_client: client.CarnectClient,
        carnect_config: carnect_settings.Config,
    ):
        self._client = carnect_client
        self._config = carnect_config
        self._logger = stdout.get_logger()

    async def cancel(self, identifier: str) -> bookings_pb2.BookingCancellation:
        provider_booking_reference = identifier
        try:
            rs_adapter = await self._cancel_booking(identifier)
        except (httpx.HTTPError, errors.CarnectCancellationError, ValueError):
            self._logger.exception(
                "Booking cancellation failed",
                identifier=identifier,
            )
            return bookings_pb2.BookingCancellation(
                provider_booking_reference=provider_booking_reference,
                status=bookings_pb2.BookingCancellation.STATUS_CANCELLATION_FAILED,
            )

        try:
            amount = await self._get_refunded_us(rs_adapter, identifier)
        except (errors.FieldMissingError, errors.CarnectCancellationError):
            self._logger.exception(
                "Failed to get total amount",
                identifier=identifier,
            )
            return bookings_pb2.BookingCancellation(
                provider_booking_reference=provider_booking_reference,
                status=bookings_pb2.BookingCancellation.STATUS_CANCELLATION_FAILED,
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
        fees = get_optional_value(
            rs_adapter.cancel_info(),
            "veh_reservation.veh_segment_core.fees.fee",
            [],
        )
        if not fees:
            raise errors.FieldMissingError(
                "Cancellation fee information is missing in cancellation response",
            )

        if fees[0].amount is None:
            raise errors.FieldMissingError(
                "Cancellation fee amount is missing in cancellation response",
            )

        if fees[0].currency_code is None:
            raise errors.FieldMissingError(
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
        builder = veh_ret_res_builder.VehRetResRqBuilder(self._config)

        id_context, surname = sequence.from_composite_id(provider_booking_reference)
        builder.unique_id().id_context(id_context)
        builder.person_name().surname(surname)

        rs_adapter = veh_ret_res_adapter.VehRetResAdapter(
            await self._client.retrieve_reservation(builder),
        )
        if not rs_adapter.is_success():
            raise errors.CarnectCancellationError(rs_adapter.get_error())

        rs_core = rs_adapter.rs_core()
        amount = get_optional_value(
            rs_core,
            "veh_reservation.veh_segment_core.total_charge.estimated_total_amount",
            None,
        )
        currency_code = get_optional_value(
            rs_core,
            "veh_reservation.veh_segment_core.total_charge.currency_code",
            None,
        )

        if amount is None:
            raise errors.FieldMissingError("missing value: total amount")
        if currency_code is None:
            raise errors.FieldMissingError("missing value: currency code")

        return money.from_string(str(amount), money.Currency(currency_code.upper()))

    async def _cancel_booking(
        self,
        provider_booking_reference: str,
    ) -> cancel_reservation_adapter.CancelReservationAdapter:
        id_context, surname = sequence.from_composite_id(provider_booking_reference)

        cancel_rq_builder = cancel_reservation_builder.CancelReservationRqBuilder(
            self._config,
        )
        cancel_info_type = cancel_rq_builder.get_cancel_info_type()
        unique_id = cancel_info_type.add_unique_id()
        unique_id.id_context(id_context)
        cancel_info_type.get_person_name().surname(surname)

        response = await self._client.cancel_reservation(cancel_rq_builder)
        rs_adapter = cancel_reservation_adapter.CancelReservationAdapter(response)

        if not rs_adapter.is_success():
            raise errors.CarnectCancellationError(rs_adapter.get_error())

        return rs_adapter
