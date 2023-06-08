import pathlib
from typing import Awaitable, Callable

import grpc

from snowfall.project.junction.provider.v1alpha import bookings_pb2, bookings_pb2_grpc
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.grpc import service

Transformer = Callable[[bytes], Awaitable[bookings_pb2.Booking]]


class NotFoundError(Exception):
    """Raised when a resource is not found."""


class Implementation(object):
    def __init__(
        self,
        storage: filesystem.Storage,
        transformer: Transformer,
    ):
        self._storage = storage
        self._transformer = transformer

    async def get(self, identifier: str) -> bookings_pb2.Booking:
        try:
            raw_booking = await self._storage.get(pathlib.Path(identifier))
        except filesystem.NotFoundError as err:
            raise NotFoundError() from err

        return await self._transformer(raw_booking)


class BookingService(service.Service, bookings_pb2_grpc.BookingServiceServicer):
    def __init__(self, implementation: Implementation):
        self._implementation = implementation
        self._logger = stdout.get_logger()

    def get_name(self) -> str:
        return bookings_pb2.DESCRIPTOR.services_by_name["BookingService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        bookings_pb2_grpc.add_BookingServiceServicer_to_server(self, server)

    async def GetBookings(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.GetBookingsRequest,
        context: grpc.aio.ServicerContext,
    ) -> bookings_pb2.GetBookingsResponse:
        booking_list: list[bookings_pb2.Booking] = []

        for booking_id in request.ids:
            try:
                booking_list.append(await self._implementation.get(booking_id))
            except NotFoundError:
                self._logger.warning("Booking not found", id=booking_id)

        return bookings_pb2.GetBookingsResponse(bookings=booking_list)

    async def MakeBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.MakeBookingRequest,
        context: grpc.aio.ServicerContext,
    ) -> bookings_pb2.MakeBookingResponse:
        return context.abort(grpc.StatusCode.UNIMPLEMENTED)
