import asyncio
import datetime
import http
import pathlib
import types as python_types
from collections.abc import Sequence
from typing import NamedTuple, Self

import orjson
import phonenumbers
from pydantic import v1 as pydantic

from snowfall.project.junction.rocket.provider import bookings
from snowfall.project.junction.rocket.provider.v1alpha import bookings_pb2
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.project.junction.rocket.service.providers.benerail import (
    cache,
    helper_models,
)
from snowfall.project.junction.rocket.service.providers.benerail.constant import (
    PROVIDER_NAME,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.benerail.client import BenerailClient
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


class _BookingError(Exception):
    """General error class for logical errors during the booking flow."""


class _OrderStateUpdateFailedError(_BookingError):
    """Raised when order status update fails."""


class _CreateBookingResponse(NamedTuple):
    booking_res: bookings_response.GetBookingResponse
    order_res: bookings_response.GetOrderResponse
    raw_booking_res: bytes


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


class Transformer:
    def __init__(self) -> None:
        self._serializer = protobuf.AnySerializer[models_pb2.Booking]()

    async def raw_to_booking(self, raw: bytes) -> bookings_pb2.Booking:
        booking = self._serializer.deserialize(raw)
        return bookings_pb2.Booking(
            id=booking.provider_booking.booking_reference,
            status=bookings_pb2.Booking.STATUS_CONFIRMED,
            provider=bookings_pb2.Booking.Provider(
                id=booking.provider_id,
                name=booking.provider_name,
            ),
            trip=bookings_pb2.Booking.Trip(
                record_locator=booking.provider_booking.record_locator,
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


class BookingCreationHandler:
    def __init__(
        self,
        benerail_client_connector: BenerailClient,
        notifications_producer: producer.Producer,
        booking_storage: filesystem.Storage,
        use_mobile_tickets: bool,  # noqa: FBT001
    ) -> None:
        self._client = benerail_client_connector
        self._notifications_producer = notifications_producer
        self._logger = stdout.get_logger()
        self._storage = booking_storage
        self._use_mobile_tickets = use_mobile_tickets

    async def create_booking(
        self,
        task: amqp_pb2.PlaceBookingTask,
        booking_offer_details: cache.BookingOfferDetails,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            create_booking_response = await self._create_booking(
                task,
                booking_offer_details,
            )
        except (errors.HttpError, _BookingError):
            self._logger.exception(
                "Failed to create booking",
                session_token=booking_offer_details.session_token,
                br_offer_id=booking_offer_details.offer_ids,
                booking_id=task.booking.id,
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR

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

        return new_booking

    async def _create_booking(  # noqa: WPS217
        self,
        task: amqp_pb2.PlaceBookingTask,
        booking_offer_details: cache.BookingOfferDetails,
    ) -> _CreateBookingResponse:
        dialogue_res = await self._client.dialogue.get_dialogue(
            booking_offer_details.dialogue_id,
        )
        total_price = str(booking_offer_details.total_price)
        etag_data = etag.EtagData(
            passenger_etags={
                pax_info.identifier: pax_info.etag
                for pax_info in booking_offer_details.passengers_info
            },
            dialogue_etag=dialogue_res.etag,
        )

        await self._update_passengers(
            dialogue_id=booking_offer_details.dialogue_id,
            passengers=task.booking.passengers,
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
        for offer_id in booking_offer_details.offer_ids:
            selected_offer_res = (
                await self._client.orders_client.add_selected_offer_to_order(
                    booking_id=booking_res.response_result.identifier,
                    order_id=order_res.response_result.identifier,
                    body=offer.SelectedOffersBody(
                        offer_id=offer_id,
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
                    amount=float(total_price),
                    currency=booking_offer_details.total_price.currency.value,
                ),
            ),
            session_token=booking_offer_details.session_token,
        )
        payment_res.set_etags(etag_data)
        await asyncio.sleep(
            min(
                _WAIT_AFTER_PAYMENT_SECONDS_PER_PAX * len(task.booking.passengers),
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
                        email=order_pax.contact_details.email,
                        phone_number="+{country_code}{national_number}".format(
                            country_code=str(
                                phonenumbers.parse(
                                    order_pax.contact_details.phone.e164_number,
                                ).country_code,
                            ),
                            national_number=str(
                                phonenumbers.parse(
                                    order_pax.contact_details.phone.e164_number,
                                ).national_number,
                            ),
                        ),
                    ),
                ),
                session_token=session_token,
            )
            res.set_etags(etag_data)


class OrdersConsumer:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.PlaceBookingTask],
        quote_cache: cache.BookingOffersCache,
        producer_obj: producer.Producer,
        booking_creation_handler: BookingCreationHandler,
        provider_id: str,
    ):
        self._cache = quote_cache
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._bookings = booking_creation_handler
        self._logger = stdout.get_logger()
        self._provider_id = provider_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.PlaceBookingTask],
    ) -> None:
        booking_offer_details = await self._cache.fetch(
            message.body.booking.trip_option.price_quote_id,
        )
        message.body.booking.provider_name = PROVIDER_NAME

        message.body.booking.provider_id = self._provider_id

        if not booking_offer_details:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=message.body.booking.id,
                key=message.body.booking.id,
            )

            return

        await self._producer.publish(
            await self._bookings.create_booking(message.body, booking_offer_details),
            routing_key="bookings.results.prices",
        )


class CancellationHandler:
    def __init__(
        self,
        booking_storage: filesystem.Storage,
        transformer: bookings.Transformer,
    ) -> None:
        self._storage = booking_storage
        self._transformer = transformer

    async def cancel(self, identifier: str) -> bookings_pb2.BookingCancellation:
        booking_raw = await self._storage.get(pathlib.Path(identifier))

        if not booking_raw:
            raise FileNotFoundError()

        booking = await self._transformer(booking_raw)
        price = next(
            price
            for price in booking.prices
            if price.type == bookings_pb2.Booking.Price.TYPE_TOTAL
        )

        price_amount = money.Money(
            amount=price.amount.units // 2,
            currency=money.Currency(price.amount.currency_code),
        )

        return bookings_pb2.BookingCancellation(
            provider_booking_reference=identifier,
            status=bookings_pb2.BookingCancellation.STATUS_REFUND_DUE,
            refunded_us=price_amount.protobuf(),
        )


def _get_title(title_enum_value: models_pb2.Passenger.Title.ValueType) -> str | None:
    if title_enum_value == models_pb2.Passenger.Title.TITLE_UNSPECIFIED:
        return None

    return (
        models_pb2.Passenger.Title.Name(title_enum_value).replace("TITLE_", "").title()
    )
