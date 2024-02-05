from unittest import mock

from snowfall.project.junction.go.service.orders import grpc
from snowfall.project.junction.go.service.orders.v1 import models_pb2, orders_pb2
from snowfall.stdlib.transport.grpc import testing


async def test_update_booking_cancellation(
    order_service_tester: testing.ServerTester,
    cancellation_request: models_pb2.CancellationRequest,
) -> None:
    with mock.patch(
        "snowfall.project.junction.go.service.orders.orders.BookingCancellationsRepository.update",
    ) as mrepository_update:
        booking_cancellation = cancellation_request.booking_cancellations[0]
        mrepository_update.return_value = models_pb2.BookingCancellation(
            id=booking_cancellation.id,
            booking_id=booking_cancellation.booking_id,
            status=models_pb2.BookingCancellation.STATUS_REFUND_ISSUED,
        )
        await order_service_tester.invoke_unary_unary(
            method=grpc.OrderService.UpdateBookingCancellation,
            request=orders_pb2.UpdateBookingCancellationRequest(
                booking_cancellation=models_pb2.BookingCancellation(
                    id=booking_cancellation.id,
                    booking_id=booking_cancellation.booking_id,
                    status=models_pb2.BookingCancellation.STATUS_REFUND_ISSUED,
                ),
            ),
        )
        mrepository_update.assert_called_with(mrepository_update.return_value)
