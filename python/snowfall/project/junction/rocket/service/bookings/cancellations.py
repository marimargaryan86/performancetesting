import asyncio
from types import MappingProxyType

import grpc

from snowfall.project.junction.rocket.provider.v1alpha import (
    bookings_pb2 as provider_bookings_pb2,
)
from snowfall.project.junction.rocket.service.bookings import repository
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.project.junction.rocket.service.gateway.v1alpha import (
    bookings_pb2,
    bookings_pb2_grpc,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.zendesk import client
from snowfall.vendor.zendesk.models import cancellation_request

_CANCELLATION_STATUS_MAP = MappingProxyType({
    provider_bookings_pb2.BookingCancellation.STATUS_UNSPECIFIED: models_pb2.BookingCancellation.STATUS_UNSPECIFIED,
    provider_bookings_pb2.BookingCancellation.STATUS_REFUND_DUE: models_pb2.BookingCancellation.STATUS_REFUND_DUE,
    provider_bookings_pb2.BookingCancellation.STATUS_NO_REFUND: models_pb2.BookingCancellation.STATUS_NO_REFUND,
    provider_bookings_pb2.BookingCancellation.STATUS_CANCELLATION_FAILED: models_pb2.BookingCancellation.STATUS_PENDING,
})


def _booking_to_zendesk_booking(
    booking: models_pb2.Booking,
) -> cancellation_request.RocketBooking:
    price = money.from_protobuf(booking.trip_option.price)
    trip_option_details = []

    for detail in booking.trip_option.details:
        result_detail_name = detail.WhichOneof("result_detail")

        if not result_detail_name:
            continue

        result_detail = getattr(detail, result_detail_name)

        if result_detail:
            trip_option_details.append(
                cancellation_request.TripOptionDetails(
                    origin_name=result_detail.origin.name,
                    destination_name=result_detail.destination.name,
                    departure_date=protobuf.protobuf_to_datetime(
                        result_detail.departure_date,
                    ).isoformat(),
                ),
            )

    return cancellation_request.RocketBooking(
        booking_id=booking.id,
        price=cancellation_request.Price(
            amount=str(price.amount),
            currency=price.currency.code,
        ),
        provider_name=booking.provider_name,
        trip_reference=booking.provider_booking.record_locator,
        operator_booking_references=[
            cancellation_request.OperatorBookingReference(
                operator_booking_reference=reference,
            )
            for reference in booking.provider_booking.operator_booking_references
        ],
        trip_option_details=trip_option_details,
        passengers=[
            cancellation_request.Passengers(
                first_name=passenger.first_name,
                last_name=passenger.last_name,
            )
            for passenger in booking.passengers
        ],
    )


def _cancellation_failed(
    cancellation_response: bookings_pb2.CancelBookingResponse,
) -> bool:
    return (
        cancellation_response.cancellation.status
        == provider_bookings_pb2.BookingCancellation.STATUS_CANCELLATION_FAILED
    )


class ManualCancellationHandler:
    def __init__(
        self,
        zendesk_client: client.ZendeskClient,
        group_id: int,
    ):
        self._zendesk_client = zendesk_client
        self._group_id = group_id

    async def cancel_booking(
        self,
        booking: models_pb2.Booking,
    ) -> int:
        payload = self._zendesk_client.create_rocket_cancel_request_payload(
            booking=_booking_to_zendesk_booking(booking),
            group_id=self._group_id,
        )

        return await self._zendesk_client.create_support_ticket(payload)


class CancellationHandler:
    def __init__(
        self,
        gateway_stub: bookings_pb2_grpc.BookingServiceStub,
        bookings: repository.BookingRepository,
        cancellations: repository.BookingCancellationRepository,
        manual_handler: ManualCancellationHandler,
    ):
        self._gateway_stub = gateway_stub
        self._bookings = bookings
        self._cancellations = cancellations
        self._manual_handler = manual_handler
        self._logger = stdout.get_logger()

    async def cancel_booking(
        self,
        booking_id: str,
        cancellation_id: str,
    ) -> None:
        booking, booking_cancellation = await self._booking_with_cancellation(
            booking_id=booking_id,
            cancellation_id=cancellation_id,
        )

        cancel_booking_response: bookings_pb2.CancelBookingResponse | None = None
        ticket_id: str | None = None

        await self._cancellations.mark_as_pending(booking_cancellation.id)

        try:
            cancel_booking_response = await self._gateway_stub.CancelBooking(
                request=bookings_pb2.CancelBookingRequest(
                    booking_id=booking.id,
                ),
            )
        except grpc.aio.AioRpcError:
            self._logger.exception("Automatic cancellation failed")

        if not cancel_booking_response or _cancellation_failed(cancel_booking_response):
            try:
                ticket_id = str(await self._manual_handler.cancel_booking(booking))
            except errors.HttpError:
                self._logger.exception("Zendesk ticket creation failed")

                return

        await self._update_booking_and_cancellation(
            booking_id=booking.id,
            booking_cancellation=booking_cancellation,
            cancel_booking_response=cancel_booking_response,
            ticket_id=ticket_id,
        )

    async def _booking_with_cancellation(
        self,
        booking_id: str,
        cancellation_id: str,
    ) -> tuple[models_pb2.Booking, models_pb2.BookingCancellation]:
        booking, cancellation = await asyncio.gather(
            self._bookings.find_by_id(booking_id),
            self._cancellations.find_by_id(cancellation_id),
        )

        if not booking or not cancellation:
            raise ValueError("Booking or cancellation not found")

        return booking, cancellation

    async def _update_booking_and_cancellation(
        self,
        booking_id: str,
        booking_cancellation: models_pb2.BookingCancellation,
        cancel_booking_response: bookings_pb2.CancelBookingResponse | None,
        ticket_id: str | None,
    ) -> None:
        if cancel_booking_response:
            await self._update_booking(booking_id, cancel_booking_response)

        await self._update_booking_cancellation(
            booking_cancellation=booking_cancellation,
            cancel_booking_response=cancel_booking_response,
            ticket_id=ticket_id,
        )

    async def _update_booking(
        self,
        booking_id: str,
        cancel_booking_response: bookings_pb2.CancelBookingResponse,
    ) -> None:
        cancelled = cancel_booking_response.cancellation.status in {
            provider_bookings_pb2.BookingCancellation.STATUS_REFUND_DUE,
            provider_bookings_pb2.BookingCancellation.STATUS_NO_REFUND,
        }

        if cancelled:
            await self._bookings.update_status(
                identifier=booking_id,
                status=models_pb2.Booking.STATUS_CANCELLED,
            )

    async def _update_booking_cancellation(
        self,
        booking_cancellation: models_pb2.BookingCancellation,
        cancel_booking_response: bookings_pb2.CancelBookingResponse | None,
        ticket_id: str | None,
    ) -> None:
        if ticket_id:
            await self._cancellations.update_ticket_id(
                identifier=booking_cancellation.id,
                ticket_id=ticket_id,
            )

            return

        if cancel_booking_response:
            booking_cancellation.status = _CANCELLATION_STATUS_MAP[
                cancel_booking_response.cancellation.status
            ]
            booking_cancellation.refunded_us.MergeFrom(
                cancel_booking_response.cancellation.refunded_us,
            )
            await self._cancellations.upsert(booking_cancellation)


class BookingCancellationsConsumer:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.HandleBookingCancellationTask],
        cancellation_handler: CancellationHandler,
    ):
        self._consumer = consumer_obj
        self._cancellation_handler = cancellation_handler

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.HandleBookingCancellationTask],
    ) -> None:
        await self._cancellation_handler.cancel_booking(
            booking_id=message.body.booking_id,
            cancellation_id=message.body.booking_cancellation_id,
        )
