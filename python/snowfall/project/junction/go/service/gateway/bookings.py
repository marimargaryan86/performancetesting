import asyncio
from collections.abc import Sequence
from typing import cast

from grpc import aio

from snowfall.project.junction.go.service.gateway import providers
from snowfall.project.junction.go.service.gateway.v1 import (
    bookings_pb2,
    bookings_pb2_grpc,
)
from snowfall.project.junction.provider.v1alpha import bookings_pb2 as providers_pb2
from snowfall.stdlib.transport.grpc import service


class Service(service.Service, bookings_pb2_grpc.BookingServiceServicer):
    def __init__(self, providers_collection: providers.Collection):
        self._providers = providers_collection

    def get_name(self) -> str:
        return bookings_pb2.DESCRIPTOR.services_by_name["BookingService"].full_name

    def register(self, server: aio.Server) -> None:
        bookings_pb2_grpc.add_BookingServiceServicer_to_server(self, server)

    async def GetBookings(  # type: ignore[override] # noqa: N802,WPS210
        self,
        request: bookings_pb2.GetBookingsRequest,
        context: aio.ServicerContext,
    ) -> bookings_pb2.GetBookingsResponse:
        group_unmarshal_results_mapping = providers.unmarshal_resource_ids(request.ids)
        bookings: list[bookings_pb2.Booking] = []
        tasks = []

        for provider_id, booking_ids in group_unmarshal_results_mapping.items():
            provider = await self._providers.find_by_id(provider_id)

            if not provider:
                continue

            tasks.append(get_bookings(provider, booking_ids))

        for task in asyncio.as_completed(tasks):
            bookings.extend(await task)

        return bookings_pb2.GetBookingsResponse(bookings=bookings)


async def get_bookings(
    provider: providers.Provider,
    booking_ids: Sequence[str],
) -> list[bookings_pb2.Booking]:
    try:
        response = cast(
            providers_pb2.GetBookingsResponse,
            await provider.connection.bookings.GetBookings(
                providers_pb2.GetBookingsRequest(ids=booking_ids),
            ),
        )
    except aio.AioRpcError:
        return []

    return [
        bookings_pb2.Booking(
            id=provider.marshal_resource_id(booking.id),
            booking=booking,
        )
        for booking in response.bookings
    ]
