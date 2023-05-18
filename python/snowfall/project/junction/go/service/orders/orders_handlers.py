from typing import Sequence

from grpc import aio

from snowfall.project.junction.go.service.orders.orders import (
    BookingsCancellationsRepository,
    JourneyRepository,
)
from snowfall.project.junction.go.service.orders.v1alpha import models_pb2, orders_pb2
from snowfall.stdlib.transport.grpc import rich_status


class CreateBookingsCancellationHandler(object):  # noqa: WPS214
    def __init__(
        self,
        request: orders_pb2.CreateBookingsCancellationRequest,
        context: aio.ServicerContext,
        journeys: JourneyRepository,
        cancellations: BookingsCancellationsRepository,
    ):
        self._request = request
        self._context = context
        self._journeys = journeys
        self._cancellations = cancellations

    async def execute(self) -> orders_pb2.CreateBookingsCancellationResponse:
        document = self._request.cancellation

        await self._validate(document)

        document.status = models_pb2.BookingsCancellation.STATUS_PENDING
        cancellation = await self._cancellations.insert(
            document,
        )

        return orders_pb2.CreateBookingsCancellationResponse(
            cancellation=cancellation,
        )

    async def _validate(  # noqa: WPS217
        self,
        document: models_pb2.BookingsCancellation,
    ) -> None:
        booking_ids = [
            cancellation.booking_id for cancellation in document.booking_cancellations
        ]
        journeys = await self._get_journeys(booking_ids)
        bookings = await self._get_bookings(journeys, booking_ids)

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
        cancellations = await self._cancellations.find_by_booking_id(
            list(booking_ids),
        )
        if [cancellation async for cancellation in cancellations]:
            await rich_status.abort_with_rich_status(
                context=self._context,
                status=rich_status.build_precondition_failure(
                    subject="booking_ids",
                    description=(
                        "One or more bookings from the provided list are already"
                        + " requested for cancellation"
                    ),
                ),
            )

    async def _get_journeys(
        self,
        booking_ids: Sequence[str],
    ) -> Sequence[models_pb2.Journey]:
        journeys_result = await self._journeys.find_by_booking_id(booking_ids)
        return [journey async for journey in journeys_result]

    async def _get_bookings(
        self,
        journeys: Sequence[models_pb2.Journey],
        booking_ids: Sequence[str],
    ) -> Sequence[models_pb2.Booking]:
        orders = [order for journey in journeys for order in journey.orders]
        return [
            booking
            for order in orders
            for booking in order.bookings
            if booking.id in booking_ids
        ]
