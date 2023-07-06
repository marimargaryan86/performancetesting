import datetime
from collections.abc import Callable
from typing import Any
from unittest import mock

import grpc
import more_itertools
import pytest
from motor import motor_asyncio

from snowfall.project.junction.go.service.gateway.v1 import (
    bookings_pb2,
    bookings_pb2_grpc,
)
from snowfall.project.junction.go.service.orders import bookings, orders
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.junction.provider.v1alpha import (
    bookings_pb2 as provider_bookings_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.testing import asserts


class MockedBookings(orders.BookingRepository):
    async def _execute(
        self,
        query: Callable[[Any], Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Do nothing."""


@pytest.fixture()
def mock_bookings(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> orders.BookingRepository:
    return MockedBookings(mongo_client.test.test)


class TestRepository(object):
    async def test_unavailable_service_returns_same_bookings(
        self,
        mock_bookings: orders.BookingRepository,
        order: models_pb2.Order,
    ) -> None:
        error = grpc.aio.AioRpcError(
            code=grpc.StatusCode.UNAVAILABLE,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        )
        stub = mock.create_autospec(bookings_pb2_grpc.BookingServiceStub)
        stub.GetBookings = mock.AsyncMock(side_effect=error)
        repo = bookings.BookingHandler(
            gateway=stub,
            fallback_bookings=mock_bookings,
        )
        latest_bookings = await repo.get_latest(order.bookings)

        await asserts.assert_iterable(
            [booking.id for booking in latest_bookings],
            [booking.id for booking in order.bookings],
        )

    async def test_not_found_returns_same_bookings(
        self,
        mock_bookings: orders.BookingRepository,
        order: models_pb2.Order,
    ) -> None:
        stub = mock.create_autospec(bookings_pb2_grpc.BookingServiceStub)
        stub.GetBookings = mock.AsyncMock(
            return_value=bookings_pb2.GetBookingsResponse(),
        )
        repo = bookings.BookingHandler(
            gateway=stub,
            fallback_bookings=mock_bookings,
        )
        latest_bookings = await repo.get_latest(order.bookings)

        await asserts.assert_iterable(
            [booking.id for booking in latest_bookings],
            [booking.id for booking in order.bookings],
        )

    async def test_updated_bookings_has_newer_updated_at(
        self,
        mock_bookings: orders.BookingRepository,
        order: models_pb2.Order,
    ) -> None:
        booking = more_itertools.first(order.bookings)
        provider_booking = provider_bookings_pb2.Booking(
            id=booking.trip_result.provider_booking_reference,
            updated_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(datetime.UTC),
            ),
        )
        stub = mock.create_autospec(bookings_pb2_grpc.BookingServiceStub)
        stub.GetBookings = mock.AsyncMock(
            return_value=bookings_pb2.GetBookingsResponse(
                bookings=[
                    bookings_pb2.Booking(
                        id=booking.id,
                        booking=provider_booking,
                    ),
                ],
            ),
        )
        repo = bookings.BookingHandler(
            gateway=stub,
            fallback_bookings=mock_bookings,
        )
        latest_bookings = await repo.get_latest(order.bookings)

        await asserts.assert_iterable(
            [booking.id for booking in latest_bookings],
            [booking.id for booking in order.bookings],
        )


class TestUpdater(object):
    async def test_booking_is_updated(
        self,
        mock_bookings: orders.BookingRepository,
        booking: models_pb2.Booking,
    ) -> None:
        provider_booking = provider_bookings_pb2.Booking(
            id=booking.id,
            updated_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(datetime.UTC),
            ),
        )
        repo = bookings.BookingHandler(
            gateway=mock.create_autospec(
                bookings_pb2_grpc.BookingServiceStub,
                spec_set=True,
            ),
            fallback_bookings=mock_bookings,
        )

        updated_booking = await repo.update_local_with_provider(
            booking,
            provider_booking,
        )
        assert protobuf.protobuf_to_datetime(
            updated_booking.updated_at,
        ) > protobuf.protobuf_to_datetime(booking.updated_at)

    async def test_booking_not_updated_when_updated_at_not_newer(
        self,
        mock_bookings: orders.BookingRepository,
        booking: models_pb2.Booking,
    ) -> None:
        provider_booking = provider_bookings_pb2.Booking(
            id=booking.id,
            updated_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=1),
            ),
        )
        repo = bookings.BookingHandler(
            gateway=mock.create_autospec(
                bookings_pb2_grpc.BookingServiceStub,
                spec_set=True,
            ),
            fallback_bookings=mock_bookings,
        )

        updated_booking = await repo.update_local_with_provider(
            booking,
            provider_booking,
        )
        assert protobuf.protobuf_to_datetime(
            updated_booking.updated_at,
        ) == protobuf.protobuf_to_datetime(booking.updated_at)

    async def test_price_is_updated(
        self,
        mock_bookings: orders.BookingRepository,
        booking: models_pb2.Booking,
    ) -> None:
        new_amount = "13.37"
        provider_booking = provider_bookings_pb2.Booking(
            id=booking.id,
            prices=[
                provider_bookings_pb2.Booking.Price(
                    type=provider_bookings_pb2.Booking.Price.TYPE_TOTAL,
                    amount=money.from_string(
                        new_amount,
                        money.Currency("EUR"),
                    ).protobuf(),
                ),
            ],
            updated_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(datetime.UTC),
            ),
        )
        repo = bookings.BookingHandler(
            gateway=mock.create_autospec(
                bookings_pb2_grpc.BookingServiceStub,
                spec_set=True,
            ),
            fallback_bookings=mock_bookings,
        )

        updated_booking = await repo.update_local_with_provider(
            booking,
            provider_booking,
        )
        assert str(money.from_protobuf(updated_booking.total_price)) == new_amount
