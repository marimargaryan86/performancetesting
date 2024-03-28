import pathlib
from collections.abc import Awaitable, Callable

import grpc

from snowfall.project.junction.rocket.provider.v1alpha import (
    bookings_pb2,
    bookings_pb2_grpc,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.grpc import service

Transformer = Callable[[bytes], Awaitable[bookings_pb2.Booking]]
CancellationHandler = Callable[[str], Awaitable[bookings_pb2.BookingCancellation]]


class NotFoundError(Exception):
    """Raised when a resource is not found."""


class Implementation(object):
    def __init__(
        self,
        storage: filesystem.Storage,
        transformer: Transformer,
        cancellation_handler: CancellationHandler | None = None,
    ):
        self._storage = storage
        self._transformer = transformer
        self._cancellation_handler = cancellation_handler

    async def get(self, identifier: str) -> bookings_pb2.Booking:
        try:
            raw_booking = await self._storage.get(pathlib.Path(identifier))
        except filesystem.NotFoundError as err:
            raise NotFoundError() from err

        return await self._transformer(raw_booking)

    async def cancel(self, identifier: str) -> bookings_pb2.BookingCancellation:
        if self._cancellation_handler is None:
            raise RuntimeError()

        return await self._cancellation_handler(identifier)

    def supports_cancellation(self) -> bool:
        return self._cancellation_handler is not None


class BookingService(service.Service, bookings_pb2_grpc.BookingServiceServicer):
    def __init__(self, implementation: Implementation):
        self._implementation = implementation
        self._logger = stdout.get_logger()

    def get_name(self) -> str:
        return bookings_pb2.DESCRIPTOR.services_by_name["BookingService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        bookings_pb2_grpc.add_BookingServiceServicer_to_server(self, server)

    async def GetBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.GetBookingRequest,
        context: grpc.aio.ServicerContext,
    ) -> bookings_pb2.GetBookingResponse:
        try:
            booking = await self._implementation.get(request.id)
        except NotFoundError:
            self._logger.warning("Booking not found", id=request.id)
            return context.abort(grpc.StatusCode.NOT_FOUND)

        return bookings_pb2.GetBookingResponse(booking=booking)

    async def MakeBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.MakeBookingRequest,
        context: grpc.aio.ServicerContext,
    ) -> bookings_pb2.MakeBookingResponse:
        return context.abort(grpc.StatusCode.UNIMPLEMENTED)

    async def CancelBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.CancelBookingRequest,
        context: grpc.aio.ServicerContext,
    ) -> bookings_pb2.CancelBookingResponse:
        if self._implementation.supports_cancellation():
            return bookings_pb2.CancelBookingResponse(
                cancellation=await self._implementation.cancel(
                    request.provider_booking_reference,
                ),
            )

        return await context.abort(grpc.StatusCode.UNIMPLEMENTED)
