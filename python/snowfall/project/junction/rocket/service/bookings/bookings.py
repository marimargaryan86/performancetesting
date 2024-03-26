import datetime
import types
from collections.abc import Sequence

import grpc

from snowfall.project.junction.rocket.provider.v1alpha import bookings_pb2
from snowfall.project.junction.rocket.service.bookings import repository
from snowfall.project.junction.rocket.service.bookings.v1alpha import models_pb2
from snowfall.project.junction.rocket.service.gateway.v1alpha import (
    bookings_pb2 as gateway_bookings_pb2,
)
from snowfall.project.junction.rocket.service.gateway.v1alpha import bookings_pb2_grpc
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
        fallback_bookings: repository.BookingRepository,
        timeout: datetime.timedelta | None = None,
    ):
        self._gateway = gateway
        self._bookings = fallback_bookings
        self._logger = stdout.get_logger()
        self._timeout = (
            timeout.total_seconds() if timeout else _GATEWAY_GRPC_TIMEOUT_SECONDS
        )

    async def get_latest(
        self,
        booking: models_pb2.Booking,
    ) -> models_pb2.Booking:
        # TODO(reuben.t): fix this to single booking
        try:
            await self._gateway.GetBooking(
                request=gateway_bookings_pb2.GetBookingRequest(
                    id="",
                ),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError:
            self._logger.warning("Gateway service not available.")
            return booking
        # TODO(reuben.t): implement local update
        return models_pb2.Booking()

    async def update_local_with_provider(
        self,
        local_booking: models_pb2.Booking,
        provider_booking: bookings_pb2.Booking,
    ) -> models_pb2.Booking:
        # TODO(reuben.t): revisit fields
        local_booking.provider_booking.ticket_urls.extend(provider_booking.ticket_urls)
        if not _provider_booking_is_newer(local_booking, provider_booking):
            return local_booking

        booking = models_pb2.Booking()
        booking.CopyFrom(local_booking)
        booking.status = _STATUS_MAPPING[provider_booking.status]
        booking.provider_id = provider_booking.provider.id
        booking.provider_name = provider_booking.provider.name
        booking.provider_booking.ClearField("ticket_urls")
        booking.provider_booking.ticket_urls.extend(provider_booking.ticket_urls)
        booking.provider_booking.booking_reference = provider_booking.id
        booking.provider_booking.record_locator = provider_booking.trip.record_locator
        booking.provider_booking.ClearField("operator_booking_references")
        booking.provider_booking.operator_booking_references.extend(
            provider_booking.trip.operator_booking_references,
        )
        _set_total_price(booking, provider_booking.prices)
        booking.provider_booking.raw_data = (
            provider_booking.raw_data or booking.provider_booking.raw_data
        )

        return await self._bookings.update(booking)


def _set_total_price(
    local_booking: models_pb2.Booking,
    prices: Sequence[bookings_pb2.Booking.Price],
) -> None:
    for price in prices:
        if price.type == bookings_pb2.Booking.Price.TYPE_TOTAL:
            local_booking.trip_option.price.CopyFrom(price.amount)

            return


def _provider_booking_is_newer(
    local_booking: models_pb2.Booking,
    provider_booking: bookings_pb2.Booking,
) -> bool:
    return protobuf.protobuf_to_datetime(
        local_booking.updated_at,
    ) < protobuf.protobuf_to_datetime(provider_booking.updated_at)
