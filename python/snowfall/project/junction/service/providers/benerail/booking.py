import asyncio
import datetime
import http
import pathlib
import types as python_types
import uuid
from collections.abc import Sequence
from typing import NamedTuple, Self

import orjson
import phonenumbers
import tenacity
from pydantic import v1 as pydantic

from snowfall.project.junction.go.service.orders.v1 import (
    amqp_pb2 as order_amqp_pb2,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.junction.provider.v1 import bookings_pb2
from snowfall.project.junction.service.providers.benerail import (
    cache,
    helper_models,
)
from snowfall.project.junction.service.providers.benerail.v1 import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.errors import BenerailError
from snowfall.vendor.benerail.models import etag
from snowfall.vendor.benerail.models.bookings import offer, order, payment
from snowfall.vendor.benerail.models.bookings import response as bookings_response
from snowfall.vendor.benerail.models.dialogue import enums as dialogue_enums
from snowfall.vendor.benerail.models.dialogue import passenger
from snowfall.vendor.benerail.models.products import enums

_GENDER_MAP = python_types.MappingProxyType(
    {
        models_pb2.Passenger.Gender.GENDER_MALE: dialogue_enums.Gender.male,
        models_pb2.Passenger.Gender.GENDER_FEMALE: dialogue_enums.Gender.female,
        models_pb2.Passenger.Gender.GENDER_UNSPECIFIED: dialogue_enums.Gender.other,
    },
)
_WAIT_AFTER_PAYMENT_SECONDS_PER_PAX = 15
_MAX_WAIT_SECONDS_AFTER_PAYMENT = 60
_PROVIDER_STATUS_MAPPING: python_types.MappingProxyType[
    enums.OrderStates,
    models_pb2.Booking.Status.ValueType,
] = python_types.MappingProxyType(
    {
        enums.OrderStates.bookable: models_pb2.Booking.STATUS_UNSPECIFIED,
        enums.OrderStates.prebooked: models_pb2.Booking.STATUS_UNSPECIFIED,
        enums.OrderStates.prerefunded: models_pb2.Booking.STATUS_UNSPECIFIED,
        enums.OrderStates.refunded_settlement_pending: (
            models_pb2.Booking.STATUS_UNSPECIFIED
        ),
        enums.OrderStates.created: models_pb2.Booking.STATUS_PENDING,
        enums.OrderStates.info_required: models_pb2.Booking.STATUS_PENDING,
        enums.OrderStates.payment_pending: models_pb2.Booking.STATUS_PENDING,
        enums.OrderStates.confirmed: models_pb2.Booking.STATUS_CONFIRMED,
        enums.OrderStates.ticketed: models_pb2.Booking.STATUS_CONFIRMED,
        enums.OrderStates.aborted: models_pb2.Booking.STATUS_ERROR,
        enums.OrderStates.order_error: models_pb2.Booking.STATUS_ERROR,
        enums.OrderStates.cancelled: models_pb2.Booking.STATUS_CANCELLED,
    },
)
_PROVIDER_BOOKING_STATUS_MAPPING: python_types.MappingProxyType[
    enums.OrderStates,
    bookings_pb2.Booking.Status.ValueType,
] = python_types.MappingProxyType(
    {
        enums.OrderStates.bookable: bookings_pb2.Booking.STATUS_UNSPECIFIED,
        enums.OrderStates.prebooked: bookings_pb2.Booking.STATUS_UNSPECIFIED,
        enums.OrderStates.prerefunded: bookings_pb2.Booking.STATUS_UNSPECIFIED,
        enums.OrderStates.refunded_settlement_pending: (
            bookings_pb2.Booking.STATUS_UNSPECIFIED
        ),
        enums.OrderStates.created: bookings_pb2.Booking.STATUS_PENDING,
        enums.OrderStates.info_required: bookings_pb2.Booking.STATUS_PENDING,
        enums.OrderStates.payment_pending: bookings_pb2.Booking.STATUS_PENDING,
        enums.OrderStates.confirmed: bookings_pb2.Booking.STATUS_CONFIRMED,
        enums.OrderStates.ticketed: bookings_pb2.Booking.STATUS_CONFIRMED,
        enums.OrderStates.aborted: bookings_pb2.Booking.STATUS_ERROR,
        enums.OrderStates.order_error: bookings_pb2.Booking.STATUS_ERROR,
        enums.OrderStates.cancelled: bookings_pb2.Booking.STATUS_CANCELLED,
    },
)


class _BookingError(Exception):
    """General error class for logical errors during the booking flow."""


class _OrderStateUpdateFailedError(_BookingError):
    """Raised when order status update fails."""


class _CreateBookingResponse(NamedTuple):
    booking_res: bookings_response.GetBookingResponse
    order_res: bookings_response.GetOrderResponse
    raw_booking_res: bytes


class Transformer(object):
    def __init__(self, provider_identifier: uuid.UUID, provider_name: str):
        self._provider_id = str(provider_identifier)
        self._provider_name = provider_name

    async def raw_to_booking(self, raw: bytes) -> bookings_pb2.Booking:
        all_results = RawStorageData.parse_from_storage(raw)

        if all_results.tickets:
            booking_status = bookings_pb2.Booking.STATUS_CONFIRMED
        else:
            booking_status = bookings_pb2.Booking.STATUS_NOT_TICKETED

        updated_at = None

        if all_results.updated_at:
            updated_at = protobuf.datetime_to_protobuf(all_results.updated_at)

        return bookings_pb2.Booking(
            id=str(all_results.booking.response_result.identifier),
            status=booking_status,
            provider=bookings_pb2.Booking.Provider(
                id=self._provider_id,
                name=self._provider_name,
            ),
            trip=bookings_pb2.Booking.Trip(
                record_locator=all_results.booking.response_result.dnr,
                operator_booking_references=[],  # TODO: Fix once we can retrieve the booking ref from benerail
            ),
            created_at=protobuf.datetime_to_protobuf(
                datetime.datetime.fromisoformat(
                    str(all_results.booking.metadata.responded_at),
                ),
            ),
            ticket_urls=all_results.tickets,
            updated_at=updated_at,
        )


class RawStorageData(pydantic.BaseModel):
    booking: bookings_response.GetBookingResponse
    tickets: list[str] | None = None
    updated_at: datetime.datetime | None = None

    @classmethod
    def parse_from_storage(cls, raw: bytes) -> Self:
        try:
            return cls.parse_raw(raw.decode())
        except ValueError:
            return cls(
                booking=bookings_response.GetBookingResponse(
                    **orjson.loads(raw),
                    dialogue_etag="",
                ),
            )


class BookingCreationHandler(object):
    def __init__(
        self,
        benerail_client: client.BenerailClient,
        notifications_producer: producer.Producer,
        booking_storage: filesystem.Storage,
    ) -> None:
        self._client = benerail_client
        self._notifications_producer = notifications_producer
        self._logger = stdout.get_logger()
        self._storage = booking_storage

    async def create_booking(
        self,
        task: order_amqp_pb2.PlaceOrderTask,
        booking_offer_details: cache.BookingOfferDetails,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            create_booking_response = await self._create_booking(
                task,
                booking_offer_details,
            )
        except (errors.HttpError, _BookingError) as ex:
            self._logger.exception(
                "Failed to create booking",
                session_token=booking_offer_details.session_token,
                br_offer_id=booking_offer_details.offer_id,
                booking_id=task.booking.id,
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = repr(ex)

            return new_booking

        new_booking.MergeFrom(
            models_pb2.Booking(
                status=(
                    _PROVIDER_STATUS_MAPPING.get(
                        enums.OrderStates(
                            create_booking_response.order_res.response_result.state,
                        ),
                        models_pb2.Booking.STATUS_UNSPECIFIED,
                    )
                    if create_booking_response.order_res.response_result.state
                    else models_pb2.Booking.STATUS_UNSPECIFIED
                ),
                provider_total_price=money.from_string(
                    string_amount=booking_offer_details.price,
                    currency=booking_offer_details.currency,
                ).protobuf(),
                trip_result=models_pb2.TripBooking(
                    provider_booking_reference=create_booking_response.booking_res.response_result.identifier,
                    record_locator=create_booking_response.booking_res.response_result.dnr,
                    created_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.now(tz=datetime.UTC),
                    ),
                ),
                raw_data=create_booking_response.raw_booking_res.decode(),
            ),
        )

        storage_data = RawStorageData(
            booking=create_booking_response.booking_res,
            updated_at=datetime.datetime.now(tz=datetime.UTC),
        )

        await self._storage.put(
            pathlib.Path(
                create_booking_response.booking_res.response_result.identifier,
            ),
            storage_data.json().encode(),
        )

        await self._notify(
            amqp_pb2.BookingNotificationTask(
                journey_id=task.metadata.journey_id,
                order_id=task.metadata.order_id,
                booking_id=task.metadata.booking_id,
                passenger_name_record=task.metadata.passenger_name_record,
                departure_at=datetime.datetime.fromisoformat(
                    booking_offer_details.departure_at,
                ).isoformat(
                    timespec="seconds",
                ),
                br_booking_id=create_booking_response.booking_res.response_result.identifier,
                br_dnr=create_booking_response.booking_res.response_result.dnr,
                br_session_token=booking_offer_details.session_token,
                created_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(datetime.UTC),
                ),
            ),
        )

        return new_booking

    async def _create_booking(  # noqa: WPS217
        self,
        task: order_amqp_pb2.PlaceOrderTask,
        booking_offer_details: cache.BookingOfferDetails,
    ) -> _CreateBookingResponse:
        dialogue_res = await self._client.dialogue.get_dialogue(
            booking_offer_details.dialogue_id,
        )
        etag_data = etag.EtagData(
            passenger_etags={
                pax_info.identifier: pax_info.etag
                for pax_info in booking_offer_details.passengers_info
            },
            dialogue_etag=dialogue_res.etag,
        )

        await self._update_passengers(
            dialogue_id=booking_offer_details.dialogue_id,
            passengers=task.passengers,
            contact_details=task.contact_details,
            etag_data=etag_data,
            br_passengers_info=booking_offer_details.passengers_info,
            session_token=booking_offer_details.session_token,
        )

        booking_res = await self._client.bookings_client.create_booking(
            dialogue_id=booking_offer_details.dialogue_id,
            etag=etag_data.dialogue_etag,
            session_token=booking_offer_details.session_token,
        )
        booking_res.set_etags(etag_data)

        order_res = await self._client.bookings_client.create_order(
            booking_id=booking_res.response_result.identifier,
            etag=etag_data.booking_etag,
            session_token=booking_offer_details.session_token,
        )
        order_res.set_etags(etag_data)

        selected_offer_res = (
            await self._client.orders_client.add_selected_offer_to_order(
                booking_id=booking_res.response_result.identifier,
                order_id=order_res.response_result.identifier,
                body=offer.SelectedOffersBody(
                    offer_id=booking_offer_details.offer_id,
                ),
                etag=etag_data.order_etag,
                session_token=booking_offer_details.session_token,
            )
        )
        selected_offer_res.set_etags(etag_data)

        order_res = await self._update_order_state(
            booking_id=booking_res.response_result.identifier,
            order_id=order_res.response_result.identifier,
            order_etag=etag_data.order_etag,
            body=order.OrderIdBody(
                state=enums.OrderStates.prebooked,
            ),
            session_token=booking_offer_details.session_token,
        )
        order_res.set_etags(etag_data)

        payment_res = await self._client.payments_client.create_payment_info_for_order(
            booking_id=booking_res.response_result.identifier,
            order_id=order_res.response_result.identifier,
            etag=etag_data.order_etag,
            body=payment.OrderIdPaymentsBody(
                payment_method=payment.PaymentMethodProp(
                    payment.PaymentMethod.ac.value,
                ),
            ),
            session_token=booking_offer_details.session_token,
        )
        payment_res.set_etags(etag_data)

        payment_res = await self._client.payments_client.confirm_order_payment(
            booking_id=booking_res.response_result.identifier,
            order_id=order_res.response_result.identifier,
            payment_id=payment_res.response_result.identifier,
            etag=etag_data.payment_etag,
            body=payment.PaymentIdBody(
                payment_method=payment.PaymentMethodProp(
                    payment.PaymentMethod.ac.value,
                ),
                amount=payment.Price(
                    amount=float(booking_offer_details.price),
                    currency=booking_offer_details.currency.value,
                ),
            ),
            session_token=booking_offer_details.session_token,
        )
        payment_res.set_etags(etag_data)
        await asyncio.sleep(
            min(
                _WAIT_AFTER_PAYMENT_SECONDS_PER_PAX * len(task.passengers),
                _MAX_WAIT_SECONDS_AFTER_PAYMENT,
            ),
        )

        booking_res, raw_response = await self._get_booking(
            booking_id=booking_res.response_result.identifier,
            session_token=booking_offer_details.session_token,
        )
        booking_res.set_etags(etag_data)
        order_res = await self._client.orders_client.get_order(
            booking_id=booking_res.response_result.identifier,
            order_id=order_res.response_result.identifier,
        )

        return _CreateBookingResponse(
            booking_res=booking_res,
            order_res=order_res,
            raw_booking_res=raw_response,
        )

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(errors.HttpStatusError),
        wait=tenacity.wait_fixed(10),
        reraise=True,
    )
    async def _get_booking(
        self,
        booking_id: str,
        session_token: str | None,
    ) -> tuple[bookings_response.GetBookingResponse, bytes]:
        return await self._client.bookings_client.get_booking(
            booking_id=booking_id,
            session_token=session_token,
        )

    async def _update_order_state(
        self,
        booking_id: str,
        order_id: str,
        order_etag: str,
        body: order.OrderIdBody,
        session_token: str | None = None,
    ) -> bookings_response.GetOrderResponse:
        try:
            return await self._client.orders_client.update_order_state(
                booking_id=booking_id,
                order_id=order_id,
                etag=order_etag,
                body=body,
                session_token=session_token,
            )
        except errors.HttpError as err:
            self._logger.info("Failed to update order state", error=str(err))

        await asyncio.sleep(5)

        order_res = await self._client.orders_client.get_order(
            booking_id=booking_id,
            order_id=order_id,
            session_token=session_token,
        )

        try:
            return await self._client.orders_client.update_order_state(
                booking_id=booking_id,
                order_id=order_id,
                etag=order_res.etag,
                body=body,
                session_token=session_token,
            )
        except errors.HttpStatusError as status_err:
            if status_err.status != http.HTTPStatus.CONFLICT:
                raise

        order_res = await self._client.orders_client.get_order(
            booking_id=booking_id,
            order_id=order_id,
            session_token=session_token,
        )

        if order_res.response_result.state == enums.OrderStates.prebooked.value:  # type: ignore[comparison-overlap]
            return order_res

        raise _OrderStateUpdateFailedError(
            "Current status: {0}".format(order_res.response_result.state),
        )

    async def _update_passengers(
        self,
        dialogue_id: str,
        passengers: Sequence[models_pb2.Passenger],
        br_passengers_info: Sequence[helper_models.PassengerInfo],
        contact_details: models_pb2.ContactDetails,
        etag_data: etag.EtagData,
        session_token: str | None = None,
    ) -> None:
        br_pax_ids_sorted = (
            pax_info.identifier
            for pax_info in sorted(
                br_passengers_info,
                key=lambda pax_info: pax_info.date_of_birth,
            )
        )
        passengers_sorted: Sequence[models_pb2.Passenger] = sorted(
            passengers,
            key=lambda pax: protobuf.protobuf_to_date(pax.date_of_birth),
        )
        number = phonenumbers.parse(contact_details.phone.e164_number)
        passengers_zip = zip(br_pax_ids_sorted, passengers_sorted, strict=True)

        for br_pax_id, order_pax in passengers_zip:
            res = await self._client.passengers_client.update_passenger(
                dialogue_id=dialogue_id,
                passenger_id=br_pax_id,
                etag=etag_data.passenger_etags[br_pax_id],
                body=passenger.PassengerRequest(
                    gender=_GENDER_MAP[order_pax.gender],
                    date_of_birth=protobuf.protobuf_to_date(order_pax.date_of_birth),
                    details=passenger.PassengerDetail(
                        title=_get_title(order_pax.title),
                        first_name=order_pax.first_name,
                        last_name=order_pax.last_name,
                        email=contact_details.email,
                        phone_number="+{country_code}{national_number}".format(
                            country_code=str(number.country_code),
                            national_number=str(number.national_number),
                        ),
                    ),
                ),
                session_token=session_token,
            )
            res.set_etags(etag_data)

    async def _notify(self, msg: amqp_pb2.BookingNotificationTask) -> None:
        await self._notifications_producer.publish(
            msg=msg,
            routing_key="benerail.notifications",
        )


class BookingCancellationHandler(object):
    def __init__(
        self,
        benerail_client: client.BenerailClient,
    ) -> None:
        self._client = benerail_client
        self._logger = stdout.get_logger()

    async def cancel_booking(self, booking_id: str) -> models_pb2.BookingCancellation:
        session_token = string.uuid()

        try:
            return await self._cancel_booking(booking_id, session_token)
        except errors.HttpError:
            self._logger.exception(
                "Booking cancellation failed",
                booking_id=booking_id,
                session_token=session_token,
            )

            return models_pb2.BookingCancellation(
                booking_id=booking_id,
                status=models_pb2.BookingCancellation.STATUS_REFUND_FAILED,
            )

    async def _cancel_booking(  # noqa: WPS217
        self,
        booking_id: str,
        session_token: str,
    ) -> models_pb2.BookingCancellation:
        booking_res = (
            await self._client.bookings_client.get_booking(
                booking_id=booking_id,
                session_token=session_token,
            )
        )[0]
        refund_order_res = await self._client.bookings_client.create_order(
            booking_id=booking_res.response_result.identifier,
            etag=booking_res.etag,
            session_token=session_token,
        )
        refund_offer_res = await self._client.orders_client.add_refund_to_order(
            booking_id=booking_res.response_result.identifier,
            order_id=refund_order_res.response_result.identifier,
            etag=refund_order_res.etag,
            body=order.OrderIdRefundOffersBody(
                fulfillment_ids=[
                    fulfillment.identifier
                    for fulfillment in booking_res.response_result.fulfillments
                ]
                if booking_res.response_result.fulfillments
                else [],
            ),
            session_token=session_token,
        )
        refund_offer_res = await self._client.orders_client.accept_refund_offer(
            booking_id=booking_id,
            order_id=refund_order_res.response_result.identifier,
            refund_offer_id=refund_offer_res.response_result.identifier,
            etag=refund_offer_res.etag,
            session_token=session_token,
        )

        # Retrieve the order again (with updated payment resource)
        refund_order_res = await self._client.orders_client.get_order(
            booking_id=booking_id,
            order_id=refund_order_res.response_result.identifier,
            session_token=session_token,
        )

        if refund_order_res.response_result.payment is None:
            raise BenerailError("Payment resource is missing from the refund order")

        payment_res = await self._client.payments_client.get_payment_resource(
            booking_id=booking_id,
            order_id=refund_order_res.response_result.identifier,
            payment_id=refund_order_res.response_result.payment.identifier,
            session_token=session_token,
        )
        payment_res = await self._client.payments_client.confirm_order_payment(
            booking_id=booking_id,
            order_id=refund_order_res.response_result.identifier,
            payment_id=payment_res.response_result.identifier,
            etag=payment_res.etag,
            body=payment.PaymentIdBody(
                payment_method=payment.PaymentMethodProp(
                    payment.PaymentMethod.ac.value,
                ),
                amount=payment_res.response_result.amount_to_pay,
            ),
            session_token=session_token,
        )

        refunded_us = None

        if refund_offer_res.response_result.total_refund_amount:
            refunded_us = money.from_string(
                currency=money.Currency(
                    refund_offer_res.response_result.total_refund_amount.currency.upper(),
                ),
                string_amount=str(
                    refund_offer_res.response_result.total_refund_amount.amount,
                ),
            )
        else:
            self._logger.error(
                "Refund amount is missing",
                payment_res=payment_res,
                session_token=session_token,
            )

        status = models_pb2.BookingCancellation.STATUS_NO_REFUND
        refunded_us_proto = None

        if refunded_us and refunded_us.amount:
            status = models_pb2.BookingCancellation.STATUS_REFUND_DUE
            refunded_us_proto = refunded_us.protobuf()

        return models_pb2.BookingCancellation(
            booking_id=booking_id,
            status=status,
            refunded_us=refunded_us_proto,
        )


def _get_title(title_enum_value: models_pb2.Passenger.Title.ValueType) -> str | None:
    if title_enum_value == models_pb2.Passenger.Title.TITLE_UNSPECIFIED:
        return None

    return (
        models_pb2.Passenger.Title.Name(title_enum_value).replace("TITLE_", "").title()
    )
