import asyncio
import dataclasses

from grpc import StatusCode, aio

from snowfall.project.junction.rocket.service.bookings import amqp, bookings
from snowfall.project.junction.rocket.service.bookings import (
    repository as booking_repositories,
)
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    grpc_pb2 as bookings_pb2,
)
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    grpc_pb2_grpc as bookings_pb2_grpc,
)
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    models_pb2,
)
from snowfall.project.junction.rocket.service.gateway.v1alpha import (
    meta_pb2_grpc,
)
from snowfall.stdlib import string
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.grpc import rich_status, service


async def _validate_cancellation(
    reseller_id: str,
    context: aio.ServicerContext,
    booking: models_pb2.Booking | None,
) -> None:
    if booking is None:
        return await context.abort(StatusCode.NOT_FOUND, "Booking not found")
    if booking.reseller_id != reseller_id:
        return await context.abort(StatusCode.PERMISSION_DENIED, "Reseller ID mismatch")
    return None


@dataclasses.dataclass(frozen=True)
class Cancellations:
    repository: booking_repositories.BookingCancellationRepository
    task_producer: amqp.BookingCancellationTaskProducer


class BookingService(
    service.Service,
    bookings_pb2_grpc.BookingServiceServicer,
):
    def __init__(
        self,
        booking_handler: bookings.BookingHandler,
        booking_repository: booking_repositories.BookingRepository,
        publisher: amqp.BookingProducer,
        default_page_size: int,
        environment: str,
        gateway_meta: meta_pb2_grpc.MetaServiceStub,
        cancellations: Cancellations,
    ):
        self._default_page_size = default_page_size
        self._booking_handler = booking_handler
        self._bookings = booking_repository
        self._cancellations = cancellations
        self._publisher = publisher
        self._environment = environment
        self._gateway_meta = gateway_meta
        self._logger = stdout.get_logger()

    def get_name(self) -> str:
        return bookings_pb2.DESCRIPTOR.services_by_name["BookingService"].full_name

    def register(self, server: aio.Server) -> None:
        bookings_pb2_grpc.add_BookingServiceServicer_to_server(self, server)

    async def MakeBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.MakeBookingRequest,
        context: aio.ServicerContext,
    ) -> bookings_pb2.MakeBookingResponse:
        if not request.reseller_id:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="reseller_id",
                    field_description="Field must not be empty",
                    description="Making a booking requires a reseller ID",
                ),
            )
        booking = await self._bookings.insert(
            document=models_pb2.Booking(
                id=string.uuid(),
                reseller_id=request.reseller_id,
                trip_option=request.trip_option,
                passengers=request.passengers,
                status=models_pb2.Booking.STATUS_PENDING,
            ),
        )
        await self._publisher.publish(
            booking=booking,
        )
        return bookings_pb2.MakeBookingResponse(booking=booking)

    async def GetBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.GetBookingRequest,
        context: aio.ServicerContext,
    ) -> bookings_pb2.GetBookingResponse:
        booking = await self._bookings.find_by_id(request.id)

        if booking is None:
            return await context.abort(StatusCode.NOT_FOUND)

        return bookings_pb2.GetBookingResponse(
            booking=await self._booking_handler.get_latest(booking),
        )

    async def ListBookings(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.ListBookingsRequest,
        context: aio.ServicerContext,
    ) -> bookings_pb2.ListBookingsResponse:
        bookings_result = await self._bookings.find(
            ids=list(request.ids.ids),
            cursor=request.page_token,
            reseller_id=request.reseller_id,
        )

        bookings_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        bookings_list = [booking async for booking in bookings_result]
        latest_bookings = await asyncio.gather(
            *[self._booking_handler.get_latest(booking) for booking in bookings_list],
        )
        return bookings_pb2.ListBookingsResponse(
            bookings=latest_bookings,
            next_page_token=await bookings_result.cursor(),
        )

    async def CreateBookingCancellation(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.CreateBookingCancellationRequest,
        context: aio.ServicerContext,
    ) -> bookings_pb2.CreateBookingCancellationResponse:
        booking = await self._bookings.find_by_id(
            request.booking_cancellation.booking_id,
        )

        await _validate_cancellation(request.reseller_id, context, booking)

        booking_cancellation = await self._save_cancellation(
            request.booking_cancellation,
        )

        await self._cancellations.task_producer.publish(
            booking_cancellation=booking_cancellation,
        )

        return bookings_pb2.CreateBookingCancellationResponse(
            booking_cancellation=booking_cancellation,
        )

    async def GetBookingCancellation(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.GetBookingCancellationRequest,
        context: aio.ServicerContext,
    ) -> bookings_pb2.GetBookingCancellationResponse:
        booking = await self._bookings.find_by_id(
            request.booking_id,
        )

        await _validate_cancellation(request.reseller_id, context, booking)

        booking_cancellation = await self._cancellations.repository.find_by_booking_id(
            request.booking_id,
        )

        if not booking_cancellation:
            return await context.abort(
                StatusCode.NOT_FOUND,
                "Booking cancellation not found",
            )

        return bookings_pb2.GetBookingCancellationResponse(
            booking_cancellation=booking_cancellation,
        )

    async def _save_cancellation(
        self,
        booking_cancellation: models_pb2.BookingCancellation,
    ) -> models_pb2.BookingCancellation:
        booking_cancellation.id = string.uuid()
        booking_cancellation.status = models_pb2.BookingCancellation.STATUS_PENDING

        return await self._cancellations.repository.insert(
            booking_cancellation,
        )
