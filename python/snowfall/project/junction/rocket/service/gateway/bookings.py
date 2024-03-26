from grpc import aio

from snowfall.project.junction.rocket.service.gateway import providers
from snowfall.project.junction.rocket.service.gateway.v1alpha import (
    bookings_pb2,
    bookings_pb2_grpc,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.grpc import service


class Service(service.Service, bookings_pb2_grpc.BookingServiceServicer):
    def __init__(self, providers_collection: providers.Collection):
        self._providers = providers_collection
        self._logger = stdout.get_logger()

    def get_name(self) -> str:
        return bookings_pb2.DESCRIPTOR.services_by_name["BookingService"].full_name

    def register(self, server: aio.Server) -> None:
        bookings_pb2_grpc.add_BookingServiceServicer_to_server(self, server)

    async def GetBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.GetBookingRequest,
        context: aio.ServicerContext,
    ) -> bookings_pb2.GetBookingResponse:
        provider = await self._providers.find_by_id(request.id)

        if not provider:
            return bookings_pb2.GetBookingResponse()

        booking = await self._get_booking(provider, request.id)

        return bookings_pb2.GetBookingResponse(booking=booking)

    async def _get_booking(
        self,
        provider: providers.Provider,
        booking_id: str,
    ) -> bookings_pb2.Booking:
        # TODO(reuben.t): replace with new fetch from provider protos

        return bookings_pb2.Booking()
