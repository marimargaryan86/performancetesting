import datetime
import pathlib

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.carnect import adapter, cache
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.carnect import client
from snowfall.vendor.carnect import config as carnect_settings
from snowfall.vendor.carnect.adapters import reservation_adapter
from snowfall.vendor.carnect.builders import reservation_builder
from snowfall.vendor.carnect.models import service

_DEFAULT_LANGUAGE = "en"


class BookingHandler(object):
    def __init__(
        self,
        carnect_client: client.CarnectClient,
        carnect_config: carnect_settings.Config,
        booking_storage: filesystem.Storage,
    ):
        self._client = carnect_client
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
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = raw_data.decode()

            return new_booking

        # TODO(hovhannes.d): send notification

        try:
            booking = self._res_adapter_to_booking(
                id_context=id_context,
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
            pathlib.Path(id_context),
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
        id_context: str,
        unique_id: str | None,
        reservation: service.VehicleReservationType,
        raw_data: bytes,
    ) -> models_pb2.Booking:
        return models_pb2.Booking(
            status=models_pb2.Booking.STATUS_CONFIRMED,
            provider_total_price=get_total_price(reservation).protobuf(),
            trip_result=models_pb2.TripBooking(
                provider_booking_reference=id_context,
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
