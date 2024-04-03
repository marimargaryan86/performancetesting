import grpc

from snowfall.project.junction.rocket.provider.v1alpha import (
    bookings_pb2 as provider_bookings_pb2,
)
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

    def register(self, server: grpc.aio.Server) -> None:
        bookings_pb2_grpc.add_BookingServiceServicer_to_server(self, server)

    async def GetBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.GetBookingRequest,
        context: grpc.aio.ServicerContext,
    ) -> bookings_pb2.GetBookingResponse:
        provider_id, _booking_id = providers.unmarshal_resource_id(request.id)
        provider = await self._providers.find_by_id(provider_id)

        if not provider:
            self._logger.warning("Unknown provider", provider_id=provider_id)
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        try:
            booking = await provider.connection.bookings.GetBooking(request.id)
        except grpc.aio.AioRpcError:
            self._logger.warning(
                "Failed to retrieve booking from provider",
                provider=provider.identifier,
            )
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return bookings_pb2.GetBookingResponse(booking=booking)

    async def CancelBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.CancelBookingRequest,
        context: grpc.aio.ServicerContext,
    ) -> bookings_pb2.CancelBookingResponse:
        ids = providers.unmarshal_resource_id(request.booking_id)

        provider = await self._providers.find_by_id(ids.provider_id)

        if not provider:
            return await context.abort(
                grpc.StatusCode.UNAVAILABLE,
                "Provider is unavailable",
            )

        if not provider.booking_capabilities.supports_cancellation:
            return await context.abort(grpc.StatusCode.UNIMPLEMENTED)

        try:
            response = await provider.connection.bookings.CancelBooking(
                provider_bookings_pb2.CancelBookingRequest(
                    provider_booking_reference=ids.resource_id,
                ),
            )
        except grpc.aio.AioRpcError as error:
            self._logger.exception("Booking cancellation failed")

            return await context.abort(
                code=grpc.StatusCode.INTERNAL,
                details=str(error),
            )

        return bookings_pb2.CancelBookingResponse(
            cancellation=response.cancellation,
        )
