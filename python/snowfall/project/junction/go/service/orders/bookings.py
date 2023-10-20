import datetime
import types
from collections.abc import Sequence

import grpc

from snowfall.project.junction.go.service.gateway.v1 import (
    bookings_pb2 as gateway_bookings_pb2,
)
from snowfall.project.junction.go.service.gateway.v1 import bookings_pb2_grpc
from snowfall.project.junction.go.service.orders import orders
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.junction.provider.v1alpha import bookings_pb2
from snowfall.stdlib import sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout

_STATUS_MAPPING = types.MappingProxyType(
    {
        bookings_pb2.Booking.STATUS_UNSPECIFIED: models_pb2.Booking.STATUS_UNSPECIFIED,
        bookings_pb2.Booking.STATUS_PENDING: models_pb2.Booking.STATUS_PENDING,
        bookings_pb2.Booking.STATUS_CONFIRMED: models_pb2.Booking.STATUS_CONFIRMED,
        bookings_pb2.Booking.STATUS_CANCELLED: models_pb2.Booking.STATUS_CANCELLED,
        bookings_pb2.Booking.STATUS_REJECTED: models_pb2.Booking.STATUS_REJECTED,
        bookings_pb2.Booking.STATUS_NOT_TICKETED: (
            models_pb2.Booking.STATUS_NOT_TICKETED
        ),
        bookings_pb2.Booking.STATUS_ERROR: models_pb2.Booking.STATUS_ERROR,
    },
)

_GATEWAY_GRPC_TIMEOUT_SECONDS = 15


class BookingHandler(object):
    def __init__(
        self,
        gateway: bookings_pb2_grpc.BookingServiceStub,
        fallback_bookings: orders.BookingRepository,
        timeout: datetime.timedelta | None = None,
    ):
        self._gateway = gateway
        self._bookings = fallback_bookings
        self._logger = stdout.get_logger()
        self._timeout = (
            timeout.total_seconds() if timeout else _GATEWAY_GRPC_TIMEOUT_SECONDS
        )

    async def get_latest(  # noqa: WPS210
        self,
        bookings: Sequence[models_pb2.Booking],
    ) -> list[models_pb2.Booking]:
        booking_mapping = {booking.id: booking for booking in bookings}
        provider_booking_map = {
            booking.trip_result.provider_booking_reference: booking
            for booking in bookings
            if (booking.provider_id and booking.trip_result.provider_booking_reference)
        }
        try:
            response = await self._gateway.GetBookings(
                request=gateway_bookings_pb2.GetBookingsRequest(
                    ids=[
                        sequence.to_composite_id(
                            [
                                booking.provider_id,
                                booking.trip_result.provider_booking_reference,
                            ],
                        )
                        for booking in provider_booking_map.values()
                    ],
                ),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError:
            self._logger.warning("Gateway service not available.")
            return list(bookings)
        for booking in response.bookings:
            _, provider_reference = sequence.from_composite_id(booking.id)

            if provider_reference not in provider_booking_map:
                continue
            local_booking = provider_booking_map[provider_reference]
            booking_mapping[local_booking.id] = await self.update_local_with_provider(
                local_booking=local_booking,
                provider_booking=booking.booking,
            )

        return list(booking_mapping.values())

    async def update_local_with_provider(
        self,
        local_booking: models_pb2.Booking,
        provider_booking: bookings_pb2.Booking,
    ) -> models_pb2.Booking:
        local_booking.ticket_urls.extend(provider_booking.ticket_urls)
        if not _provider_booking_is_newer(local_booking, provider_booking):
            return local_booking

        booking = models_pb2.Booking()
        booking.CopyFrom(local_booking)
        booking.status = _STATUS_MAPPING[provider_booking.status]
        booking.provider_id = provider_booking.provider.id
        booking.provider_name = provider_booking.provider.name
        booking.ClearField("ticket_urls")
        booking.ticket_urls.extend(provider_booking.ticket_urls)
        booking.trip_result.provider_booking_reference = provider_booking.id
        booking.trip_result.record_locator = provider_booking.trip.record_locator
        booking.trip_result.ClearField("operator_booking_references")
        booking.trip_result.operator_booking_references.extend(
            provider_booking.trip.operator_booking_references,
        )
        _set_total_price(booking, provider_booking.prices)
        booking.raw_data = provider_booking.raw_data or booking.raw_data

        return await self._bookings.update(booking)


def _set_total_price(
    local_booking: models_pb2.Booking,
    prices: Sequence[bookings_pb2.Booking.Price],
) -> None:
    for price in prices:
        if price.type == bookings_pb2.Booking.Price.TYPE_TOTAL:
            local_booking.total_price.CopyFrom(price.amount)

            return


def _provider_booking_is_newer(
    local_booking: models_pb2.Booking,
    provider_booking: bookings_pb2.Booking,
) -> bool:
    return protobuf.protobuf_to_datetime(
        local_booking.updated_at,
    ) < protobuf.protobuf_to_datetime(provider_booking.updated_at)
