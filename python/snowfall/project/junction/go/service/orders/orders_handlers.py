from collections.abc import Sequence

from grpc import StatusCode, aio

from snowfall.project.junction.go.service.orders.orders import (
    BookingRepository,
    CancellationRequestsRepository,
    JourneyRepository,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2, orders_pb2
from snowfall.project.junction.go.service.orders.zendesk.client import ZendeskClient
from snowfall.stdlib.transport.grpc import rich_status
from snowfall.stdlib.transport.http.errors import HttpStatusError


class CreateCancellationRequestHandler(object):
    def __init__(
        self,
        request: orders_pb2.CreateCancellationRequestRequest,
        context: aio.ServicerContext,
        journeys: JourneyRepository,
        cancellations: CancellationRequestsRepository,
        zendesk_client: ZendeskClient,
        cancellation_group_id: int,
    ):
        self._request = request
        self._context = context
        self._journeys = journeys
        self._cancellations = cancellations
        self._zendesk_client = zendesk_client
        self._cancellation_group_id = cancellation_group_id

    async def execute(
        self,
    ) -> orders_pb2.CreateCancellationRequestResponse:
        document = self._request.cancellation_request

        booking_ids = [
            cancellation.booking_id for cancellation in document.booking_cancellations
        ]
        journeys = await self._get_journeys(booking_ids)
        bookings_and_orders = await self._extract_bookings_and_orders(
            journeys,
            booking_ids,
        )
        bookings = [booking for booking, _, _ in bookings_and_orders.values()]

        await self._validate(booking_ids, journeys, bookings)

        for cancellation in document.booking_cancellations:
            booking, order, journey = bookings_and_orders[cancellation.booking_id]
            ticket_id = await self._create_zendesk_support_ticket(
                booking,
                order,
                journey,
            )
            cancellation.ticket_id = ticket_id
            cancellation.status = models_pb2.BookingCancellation.STATUS_PENDING

        document.status = models_pb2.CancellationRequest.STATUS_PENDING
        cancellation_request = await self._cancellations.insert(
            document,
        )

        return orders_pb2.CreateCancellationRequestResponse(
            cancellation_request=cancellation_request,
        )

    async def _validate(
        self,
        booking_ids: Sequence[str],
        journeys: Sequence[models_pb2.Journey],
        bookings: Sequence[models_pb2.Booking],
    ) -> None:
        await self._validate_bookings_not_empty(booking_ids)
        await self._validate_bookings_belong_to_reseller(journeys)
        await self._validate_bookings_exist(bookings, booking_ids)
        await self._validate_bookings_statuses(bookings)
        await self._validate_not_duplication(booking_ids)

    async def _validate_bookings_not_empty(self, booking_ids: Sequence[str]) -> None:
        if not booking_ids:
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description="At least one booking ID should be provided",
                ),
            )

    async def _validate_bookings_belong_to_reseller(
        self,
        journeys: Sequence[models_pb2.Journey],
    ) -> None:
        reseller_id = self._request.cancellation_request.reseller_id
        bookings_belong_to_reseller = all(
            reseller_id == journey.reseller_id for journey in journeys
        )
        if not bookings_belong_to_reseller:
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description="Some of the bookings aren't found",
                ),
            )

    async def _validate_bookings_exist(
        self,
        bookings: Sequence[models_pb2.Booking],
        booking_ids: Sequence[str],
    ) -> None:
        if len(bookings) != len(booking_ids):
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description="Some of the bookings aren't found",
                ),
            )

    async def _validate_bookings_statuses(
        self,
        bookings: Sequence[models_pb2.Booking],
    ) -> None:
        allowed_statuses = [
            models_pb2.Booking.STATUS_CONFIRMED,
            models_pb2.Booking.STATUS_NOT_TICKETED,
        ]

        if not all(booking.status in allowed_statuses for booking in bookings):
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description="One of the bookings is in inappropriate status",
                ),
            )

    async def _validate_not_duplication(self, booking_ids: Sequence[str]) -> None:
        cancellations = await self._cancellations.find_by_booking_ids(
            list(booking_ids),
        )
        if [cancellation async for cancellation in cancellations]:
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description=(
                        "One or more bookings from the provided list are already"
                        " requested for cancellation"
                    ),
                ),
            )

    async def _get_journeys(
        self,
        booking_ids: Sequence[str],
    ) -> Sequence[models_pb2.Journey]:
        journeys_result = await self._journeys.find_by_booking_id(booking_ids)
        return [journey async for journey in journeys_result]

    async def _extract_bookings_and_orders(
        self,
        journeys: Sequence[models_pb2.Journey],
        booking_ids: Sequence[str],
    ) -> dict[str, tuple[models_pb2.Booking, models_pb2.Order, models_pb2.Journey]]:
        return {  # noqa: WPS224
            booking.id: (booking, order, journey)
            for journey in journeys
            for order in journey.orders
            for booking in order.bookings
            if booking.id in booking_ids
        }

    async def _create_zendesk_support_ticket(
        self,
        booking: models_pb2.Booking,
        order: models_pb2.Order,
        journey: models_pb2.Journey,
    ) -> str:
        try:
            ticket_id = await self._zendesk_client.create_support_ticket(
                payload=self._zendesk_client.create_cancel_request_payload(
                    booking,
                    order,
                    journey,
                    self._cancellation_group_id,
                ),
            )
        except HttpStatusError as exc:
            error_msg = (
                "Zendesk support ticket creation failed with status code: {0}".format(
                    exc.status,
                )
            )
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="zendesk_client",
                    description=error_msg,
                ),
            )

        return str(ticket_id)


class CancellationTicketCompletedHandler(object):
    def __init__(
        self,
        request: orders_pb2.HandleCancellationTicketCompletedRequest,
        context: aio.ServicerContext,
        bookings: BookingRepository,
        cancellations: CancellationRequestsRepository,
    ):
        self._request = request
        self._context = context
        self._bookings = bookings
        self._cancellations = cancellations

    async def execute(self) -> orders_pb2.HandleCancellationTicketCompletedResponse:
        cancellation_request = await self._cancellations.find_by_ticket_id(
            ticket_id=self._request.ticket_id,
        )

        if not cancellation_request:
            return await self._context.abort(StatusCode.NOT_FOUND)

        booking_cancellation = next(
            booking_cancellation
            for booking_cancellation in cancellation_request.booking_cancellations
            if booking_cancellation.ticket_id == self._request.ticket_id
        )
        ticket_status = self._request.status

        match ticket_status:
            case orders_pb2.Status.STATUS_REJECTED:
                booking_cancellation.status = (
                    models_pb2.BookingCancellation.STATUS_REJECTED
                )
            case orders_pb2.Status.STATUS_NO_REFUND:
                booking_cancellation.status = (
                    models_pb2.BookingCancellation.STATUS_NO_REFUND
                )
                await self._update_booking_status(
                    booking_id=booking_cancellation.booking_id,
                )
            case orders_pb2.Status.STATUS_REFUND_DUE:
                booking_cancellation.status = (
                    models_pb2.BookingCancellation.STATUS_REFUND_DUE
                )
                await self._update_booking_status(
                    booking_id=booking_cancellation.booking_id,
                )
                # TODO: Create refund in PAY.

        self._update_overall_cancellation_status(cancellation_request)
        await self._cancellations.update(document=cancellation_request)

        return orders_pb2.HandleCancellationTicketCompletedResponse(
            booking_cancellation=booking_cancellation,
        )

    async def _update_booking_status(
        self,
        booking_id: str,
    ) -> None:
        booking = await self._bookings.find_by_id(document_id=booking_id)

        if booking is None:
            await self._context.abort(StatusCode.NOT_FOUND)
            return

        booking.status = models_pb2.Booking.STATUS_CANCELLED
        await self._bookings.update(booking)

    def _update_overall_cancellation_status(
        self,
        cancellation: models_pb2.CancellationRequest,
    ) -> None:
        all_bookings_cancelled = all(
            booking_cancellation.status
            in {
                models_pb2.BookingCancellation.STATUS_COMPLETED,
                models_pb2.BookingCancellation.STATUS_REJECTED,
                models_pb2.BookingCancellation.STATUS_REFUND_DUE,
                models_pb2.BookingCancellation.STATUS_NO_REFUND,
            }
            for booking_cancellation in cancellation.booking_cancellations
        )

        if all_bookings_cancelled:
            cancellation.status = models_pb2.CancellationRequest.STATUS_COMPLETED
