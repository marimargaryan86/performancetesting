from collections.abc import Sequence

from grpc import StatusCode, aio

from snowfall.project.junction.go.service.orders.orders import (
    BookingRepository,
    BookingsCancellationsRepository,
    JourneyRepository,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2, orders_pb2
from snowfall.project.junction.go.service.orders.zendesk.client import ZendeskClient
from snowfall.stdlib.transport.grpc import rich_status
from snowfall.stdlib.transport.http.errors import HttpStatusError


class CreateBookingsCancellationHandler(object):  # noqa: WPS214
    def __init__(  # noqa: WPS211
        self,
        request: orders_pb2.CreateBookingsCancellationRequest,
        context: aio.ServicerContext,
        journeys: JourneyRepository,
        cancellations: BookingsCancellationsRepository,
        zendesk_client: ZendeskClient,
    ):
        self._request = request
        self._context = context
        self._journeys = journeys
        self._cancellations = cancellations
        self._zendesk_client = zendesk_client

    async def execute(  # noqa: WPS210
        self,
    ) -> orders_pb2.CreateBookingsCancellationResponse:
        document = self._request.cancellation

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

        for booking_cancellation in document.booking_cancellations:
            booking, order, journey = bookings_and_orders.get(  # type: ignore[misc]
                booking_cancellation.booking_id,
            )
            ticket_id = await self._create_zendesk_support_ticket(
                booking,
                order,
                journey,
            )
            booking_cancellation.ticket_id = ticket_id
            booking_cancellation.status = models_pb2.BookingCancellation.STATUS_PENDING

        document.status = models_pb2.BookingsCancellation.STATUS_PENDING
        cancellation = await self._cancellations.insert(
            document,
        )

        return orders_pb2.CreateBookingsCancellationResponse(
            cancellation=cancellation,
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
        reseller_id = self._request.cancellation.reseller_id
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


class UpdateBookingCancellationHandler(object):
    def __init__(
        self,
        request: orders_pb2.UpdateBookingCancellationRequest,
        context: aio.ServicerContext,
        bookings: BookingRepository,
        cancellations: BookingsCancellationsRepository,
    ):
        self._request = request
        self._context = context
        self._bookings = bookings
        self._cancellations = cancellations

    async def execute(self) -> orders_pb2.UpdateBookingCancellationResponse:
        cancellation = await self._cancellations.find_by_booking_cancellation_id(
            booking_cancellation_id=self._request.id,
        )

        if (  # noqa: WPS337
            cancellation is None
            or cancellation.reseller_id != self._request.reseller_id
        ):
            await self._context.abort(StatusCode.NOT_FOUND)

        booking_cancellation = next(
            booking_cancellation
            for booking_cancellation in cancellation.booking_cancellations  # type: ignore[union-attr]
            if booking_cancellation.id == self._request.id
        )

        if (  # noqa: WPS337
            self._request.status
            == orders_pb2.UpdateBookingCancellationRequest.Status.STATUS_COMPLETED
        ):
            await self._update_booking_status(booking_cancellation.booking_id)

        booking_cancellation.status = self._request.status
        self._update_overall_cancellation_status(cancellation)  # type: ignore[arg-type]

        await self._cancellations.update(document=cancellation)  # type: ignore[arg-type]

        return orders_pb2.UpdateBookingCancellationResponse(
            cancellation=booking_cancellation,
        )

    async def _update_booking_status(
        self,
        booking_id: str,
    ) -> None:
        booking = await self._bookings.find_by_id(
            document_id=booking_id,
        )

        if booking is None:
            await self._context.abort(StatusCode.NOT_FOUND)

        booking.status = models_pb2.Booking.STATUS_CANCELLED  # type: ignore[union-attr]
        await self._bookings.update(booking)  # type: ignore[arg-type]

    def _update_overall_cancellation_status(
        self,
        cancellation: models_pb2.BookingsCancellation,
    ) -> None:
        all_bookings_cancelled = all(
            booking_cancellation.status
            == models_pb2.BookingCancellation.STATUS_COMPLETED
            for booking_cancellation in cancellation.booking_cancellations
        )

        if all_bookings_cancelled:
            cancellation.status = models_pb2.BookingsCancellation.STATUS_COMPLETED
