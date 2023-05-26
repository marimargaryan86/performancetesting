from grpc import StatusCode, aio

from snowfall.project.junction.go.service.gateway import providers
from snowfall.project.junction.provider.v1alpha import bookings_pb2, bookings_pb2_grpc
from snowfall.stdlib.transport.grpc import service


class BookingService(service.Service, bookings_pb2_grpc.BookingServiceServicer):
    def __init__(self, providers_collection: providers.Collection):
        self._providers = providers_collection

    def get_name(self) -> str:
        return bookings_pb2.DESCRIPTOR.services_by_name["BookingService"].full_name

    def register(self, server: aio.Server) -> None:
        bookings_pb2_grpc.add_BookingServiceServicer_to_server(self, server)

    async def GetBookings(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.GetBookingsRequest,
        context: aio.ServicerContext,
    ) -> bookings_pb2.GetBookingsResponse:
        group_unmarshal_results_mapping = providers.unmarshal_resource_ids(request.ids)
        bookings: list[bookings_pb2.Booking] = []

        for provider_id in group_unmarshal_results_mapping:
            provider = self._providers.find_by_id(provider_id)

            if not provider:
                continue

            # TODO: fetch bookings from provider
            bookings.extend([])

        return bookings_pb2.GetBookingsResponse(bookings=bookings)

    async def MakeBooking(  # type: ignore[override] # noqa: N802
        self,
        request: bookings_pb2.MakeBookingRequest,
        context: aio.ServicerContext,
    ) -> bookings_pb2.MakeBookingResponse:
        return context.abort(StatusCode.UNIMPLEMENTED)
