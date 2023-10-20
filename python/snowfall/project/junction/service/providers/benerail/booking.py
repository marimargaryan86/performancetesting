import asyncio
import datetime
import pathlib
import types as python_types
import uuid
from collections.abc import Sequence

import more_itertools
import orjson
import phonenumbers
import tenacity

from snowfall.project.junction.go.service.orders.v1 import (
    amqp_pb2 as order_amqp_pb2,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.junction.provider.v1alpha import bookings_pb2
from snowfall.project.junction.service.providers.benerail import (
    cache,
    helper_functions,
    helper_models,
)
from snowfall.project.junction.service.providers.benerail.v1alpha import amqp_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models import etag
from snowfall.vendor.benerail.models.bookings import offer, order, payment
from snowfall.vendor.benerail.models.bookings import response as booking_response
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


class Enricher(object):
    def __init__(self, benerail_client: client.BenerailClient):
        self._client = benerail_client
        self._logger = stdout.get_logger()

    async def enrich(
        self,
        booking: bookings_pb2.Booking,
    ) -> bookings_pb2.Booking:
        try:
            booking_res, _ = await self._client.bookings_client.get_booking(
                booking_id=booking.id,
            )
        except errors.HttpError:
            self._logger.exception("Failed to fetch the booking")

            return booking

        order_res = await self._client.orders_client.get_order(
            booking_id=booking.id,
            order_id=helper_functions.last_id_of_url(
                more_itertools.first(booking_res.response_result.orders or []).href,
            ),
        )

        booking.MergeFrom(
            bookings_pb2.Booking(
                status=(
                    _PROVIDER_BOOKING_STATUS_MAPPING.get(
                        enums.OrderStates(order_res.response_result.state),
                        bookings_pb2.Booking.STATUS_UNSPECIFIED,
                    )
                    if order_res.response_result.state
                    else bookings_pb2.Booking.STATUS_UNSPECIFIED
                ),
                updated_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC),
                ),
            ),
        )

        if booking_res.response_result.fulfillments:
            ticket_urls = (
                await self._client.bookings_client.get_ticket_urls_from_fulfillment(
                    booking_id=booking_res.response_result.identifier,
                    fulfillment_id=helper_functions.last_id_of_url(
                        booking_res.response_result.fulfillments[0].href,
                    ),
                )
            )

            booking.ticket_urls.extend(ticket_urls)

        return booking


class Transformer(object):
    def __init__(self, provider_identifier: uuid.UUID, provider_name: str):
        self._provider_id = str(provider_identifier)
        self._provider_name = provider_name

    async def raw_to_booking(self, raw: bytes) -> bookings_pb2.Booking:
        booking_result = booking_response.GetBookingResponse(
            **orjson.loads(raw),
            dialogue_etag="",
        )

        # TODO: How to figure out real status?
        booking_status = bookings_pb2.Booking.STATUS_NOT_TICKETED

        return bookings_pb2.Booking(
            id=str(booking_result.response_result.identifier),
            status=booking_status,
            provider=bookings_pb2.Booking.Provider(
                id=self._provider_id,
                name=self._provider_name,
            ),
            trip=bookings_pb2.Booking.Trip(
                record_locator=booking_result.response_result.dnr,
                operator_booking_references=[booking_result.response_result.identifier],
            ),
            created_at=protobuf.datetime_to_protobuf(
                datetime.datetime.fromisoformat(
                    str(booking_result.metadata.responded_at),
                ),
            ),
            # TODO: No idea how to get updated_at from the booking model.
        )


class BookingHandler(object):
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

    async def create_booking(  # noqa: WPS210, WPS213, WPS217
        self,
        task: order_amqp_pb2.PlaceOrderTask,
        booking_offer_details: cache.BookingOfferDetails,
    ) -> models_pb2.Booking:
        new_booking = task.booking
        etag_data = etag.EtagData(
            passenger_etags={
                pax_info.identifier: pax_info.etag
                for pax_info in booking_offer_details.passengers_info
            },
            dialogue_etag=booking_offer_details.dialogue_info.etag,
        )

        await self._update_passengers(
            dialogue_id=booking_offer_details.dialogue_info.identifier,
            passengers=task.passengers,
            contact_details=task.contact_details,
            etag_data=etag_data,
            br_passengers_info=booking_offer_details.passengers_info,
        )

        booking_res = await self._client.bookings_client.create_booking(
            dialogue_id=booking_offer_details.dialogue_info.identifier,
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
        await self._storage.put(
            pathlib.Path(
                booking_res.response_result.identifier,
            ),
            raw_response,
        )
        order_res = await self._client.orders_client.get_order(
            booking_id=booking_res.response_result.identifier,
            order_id=order_res.response_result.identifier,
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
                br_booking_id=booking_res.response_result.identifier,
                br_dnr=booking_res.response_result.dnr,
                br_session_token=booking_offer_details.session_token,
                created_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(datetime.UTC),
                ),
            ),
        )

        new_booking.MergeFrom(
            models_pb2.Booking(
                status=(
                    _PROVIDER_STATUS_MAPPING.get(
                        enums.OrderStates(order_res.response_result.state),
                        models_pb2.Booking.STATUS_UNSPECIFIED,
                    )
                    if order_res.response_result.state
                    else models_pb2.Booking.STATUS_UNSPECIFIED
                ),
                provider_total_price=money.from_string(
                    string_amount=booking_offer_details.price,
                    currency=booking_offer_details.currency,
                ).protobuf(),
                trip_result=models_pb2.TripBooking(
                    provider_booking_reference=booking_res.response_result.identifier,
                    record_locator=booking_res.response_result.dnr,
                    created_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.now(tz=datetime.UTC),
                    ),
                ),
                raw_data=booking_res.json(),
            ),
        )

        return new_booking

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(2),
        retry=tenacity.retry_if_exception_type(errors.HttpStatusError),
        wait=tenacity.wait_fixed(5),
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

    async def _update_order_state(  # noqa: WPS211
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
        except errors.HttpStatusError as err:
            self._logger.info("Failed to update order state", error=str(err))

        await asyncio.sleep(5)

        order_res = await self._client.orders_client.get_order(booking_id, order_id)

        return await self._client.orders_client.update_order_state(
            booking_id=booking_id,
            order_id=order_id,
            etag=order_res.order_etag,
            body=body,
            session_token=session_token,
        )

    async def _update_passengers(  # noqa: WPS210,WPS211
        self,
        dialogue_id: str,
        passengers: Sequence[models_pb2.Passenger],
        br_passengers_info: Sequence[helper_models.PassengerInfo],
        contact_details: models_pb2.ContactDetails,
        etag_data: etag.EtagData,
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
            )
            res.set_etags(etag_data)

    async def _notify(self, msg: amqp_pb2.BookingNotificationTask) -> None:
        await self._notifications_producer.publish(
            msg=msg,
            routing_key="benerail.notifications",
        )


def _get_title(title_enum_value: models_pb2.Passenger.Title.ValueType) -> str | None:
    if title_enum_value == models_pb2.Passenger.Title.TITLE_UNSPECIFIED:
        return None

    return (
        models_pb2.Passenger.Title.Name(title_enum_value).replace("TITLE_", "").title()
    )
