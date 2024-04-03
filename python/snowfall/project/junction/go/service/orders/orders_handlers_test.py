from unittest import mock

from grpc import StatusCode

from snowfall.project.junction.go.service.orders import orders, smtp
from snowfall.project.junction.go.service.orders.orders_handlers import (
    CancellationTicketCompletedHandler,
)
from snowfall.project.junction.go.service.orders.v1 import models_pb2, orders_pb2
from snowfall.project.pay.adapter import refunds as refunds_adapter


class TestCancellationTicketCompletedHandler:
    async def test_ticket_not_exists(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        booking_repository: orders.BookingRepository,
        order_repository: orders.OrderRepository,
        journey_repository: orders.JourneyRepository,
    ) -> None:
        smtp_client = mock.AsyncMock()

        handler, context = self._create_handler(
            ticket_id="non_existing",
            status=orders_pb2.Status.STATUS_NO_REFUND,
            booking_repository=booking_repository,
            cancellation_requests_repository=cancellation_requests_repository,
            order_repository=order_repository,
            journey_repository=journey_repository,
            smtp_client=smtp_client,
        )

        await handler.execute()

        context.abort.assert_awaited_with(StatusCode.NOT_FOUND)

    async def test_ticket_no_refund(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        booking_repository: orders.BookingRepository,
        order_repository: orders.OrderRepository,
        journey_repository: orders.JourneyRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        booking_cancellation = cancellation_request.booking_cancellations[0]
        smtp_client = mock.AsyncMock()
        handler, _ = self._create_handler(
            ticket_id=booking_cancellation.ticket_id,
            status=orders_pb2.Status.STATUS_NO_REFUND,
            booking_repository=booking_repository,
            cancellation_requests_repository=cancellation_requests_repository,
            order_repository=order_repository,
            journey_repository=journey_repository,
            smtp_client=smtp_client,
        )
        with (
            mock.patch(
                "snowfall.project.junction.go.service.orders.orders_handlers.cancel_confirmation.send_cancel_confirmation",
            ),
            mock.patch.object(booking_repository, "update") as update_mock,
        ):
            await handler.execute()

        assert (
            update_mock.call_args[0][0].status
            == models_pb2.Booking.Status.STATUS_CANCELLED
        )

        updated_cancellation = await cancellation_requests_repository.find_by_id(
            cancellation_request.id,
        )
        assert updated_cancellation

        updated_booking_cancellation = next(
            elem
            for elem in updated_cancellation.booking_cancellations
            if elem.ticket_id == booking_cancellation.ticket_id
        )

        assert (
            updated_cancellation.status == models_pb2.CancellationRequest.STATUS_PENDING
        )
        assert (
            updated_booking_cancellation.status
            == models_pb2.BookingCancellation.STATUS_NO_REFUND
        )

    async def test_ticket_refund_due(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        booking_repository: orders.BookingRepository,
        cancellation_request: models_pb2.CancellationRequest,
        order_repository: orders.OrderRepository,
        journey_repository: orders.JourneyRepository,
    ) -> None:
        booking_cancellation = cancellation_request.booking_cancellations[0]
        refund_client = mock.AsyncMock()
        smtp_client = mock.AsyncMock()
        handler, _ = self._create_handler(
            ticket_id=booking_cancellation.ticket_id,
            status=orders_pb2.Status.STATUS_REFUND_DUE,
            booking_repository=booking_repository,
            cancellation_requests_repository=cancellation_requests_repository,
            refund_client=refund_client,
            order_repository=order_repository,
            journey_repository=journey_repository,
            smtp_client=smtp_client,
        )

        with (
            mock.patch(
                "snowfall.project.junction.go.service.orders.orders_handlers.cancel_confirmation.send_cancel_confirmation",
                new_callable=mock.AsyncMock,
            ) as mock_send_cancel,
            mock.patch.object(
                booking_repository,
                "update",
            ) as update_mock,
        ):
            await handler.execute()
            mock_send_cancel.assert_called()

        assert (
            update_mock.call_args[0][0].status
            == models_pb2.Booking.Status.STATUS_CANCELLED
        )

        updated_cancellation = await cancellation_requests_repository.find_by_id(
            cancellation_request.id,
        )
        assert updated_cancellation

        updated_booking_cancellation = next(
            elem
            for elem in updated_cancellation.booking_cancellations
            if elem.ticket_id == booking_cancellation.ticket_id
        )

        assert (
            updated_cancellation.status == models_pb2.CancellationRequest.STATUS_PENDING
        )
        assert (
            updated_booking_cancellation.status
            == models_pb2.BookingCancellation.STATUS_REFUND_DUE
        )
        refund_client.create.assert_awaited()

    async def test_ticket_rejected(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        booking_repository: orders.BookingRepository,
        cancellation_request: models_pb2.CancellationRequest,
        order_repository: orders.OrderRepository,
        journey_repository: orders.JourneyRepository,
    ) -> None:
        booking_cancellation = cancellation_request.booking_cancellations[0]
        smtp_client = mock.AsyncMock()
        handler, _ = self._create_handler(
            ticket_id=booking_cancellation.ticket_id,
            status=orders_pb2.Status.STATUS_REJECTED,
            booking_repository=booking_repository,
            cancellation_requests_repository=cancellation_requests_repository,
            order_repository=order_repository,
            journey_repository=journey_repository,
            smtp_client=smtp_client,
        )
        with (
            mock.patch(
                "snowfall.project.junction.go.service.orders.orders_handlers.cancel_confirmation.send_cancel_confirmation",
                new_callable=mock.AsyncMock,
            ),
            mock.patch.object(booking_repository, "update") as update_mock,
        ):
            await handler.execute()

        update_mock.assert_not_awaited()

        updated_cancellation = await cancellation_requests_repository.find_by_id(
            cancellation_request.id,
        )
        assert updated_cancellation

        updated_booking_cancellation = next(
            elem
            for elem in updated_cancellation.booking_cancellations
            if elem.ticket_id == booking_cancellation.ticket_id
        )

        assert (
            updated_cancellation.status == models_pb2.CancellationRequest.STATUS_PENDING
        )
        assert (
            updated_booking_cancellation.status
            == models_pb2.BookingCancellation.STATUS_REJECTED
        )

    async def test_overall_status_completed(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        booking_repository: orders.BookingRepository,
        cancellation_request: models_pb2.CancellationRequest,
        order_repository: orders.OrderRepository,
        journey_repository: orders.JourneyRepository,
    ) -> None:
        booking_cancellation1 = cancellation_request.booking_cancellations[0]
        booking_cancellation2 = cancellation_request.booking_cancellations[1]
        smtp_client = mock.AsyncMock()
        handler1, _ = self._create_handler(
            ticket_id=booking_cancellation1.ticket_id,
            status=orders_pb2.Status.STATUS_REJECTED,
            booking_repository=booking_repository,
            cancellation_requests_repository=cancellation_requests_repository,
            order_repository=order_repository,
            journey_repository=journey_repository,
            smtp_client=smtp_client,
        )
        handler2, _ = self._create_handler(
            ticket_id=booking_cancellation2.ticket_id,
            status=orders_pb2.Status.STATUS_NO_REFUND,
            booking_repository=booking_repository,
            cancellation_requests_repository=cancellation_requests_repository,
            order_repository=order_repository,
            journey_repository=journey_repository,
            smtp_client=smtp_client,
        )
        with (
            mock.patch(
                "snowfall.project.junction.go.service.orders.orders_handlers.cancel_confirmation.send_cancel_confirmation",
                new_callable=mock.AsyncMock,
            ) as mock_send_cancel,
            mock.patch.object(booking_repository, "update"),
        ):
            await handler1.execute()
            await handler2.execute()
            mock_send_cancel.assert_called()

        updated_cancellation = await cancellation_requests_repository.find_by_id(
            cancellation_request.id,
        )
        assert updated_cancellation

        assert (
            updated_cancellation.status
            == models_pb2.CancellationRequest.STATUS_COMPLETED
        )

    def _create_handler(
        self,
        ticket_id: str,
        status: orders_pb2.Status.ValueType,
        booking_repository: orders.BookingRepository,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        order_repository: orders.OrderRepository,
        journey_repository: orders.JourneyRepository,
        smtp_client: smtp.EmailClient,
        refund_client: refunds_adapter.Client | None = None,
        environment: str = "test_env",
    ) -> tuple[CancellationTicketCompletedHandler, mock.AsyncMock]:
        context = mock.AsyncMock()

        request = orders_pb2.HandleCancellationTicketCompletedRequest(
            ticket_id=ticket_id,
            status=status,
        )

        handler = CancellationTicketCompletedHandler(
            request=request,
            context=context,
            bookings=booking_repository,
            cancellations=cancellation_requests_repository,
            refund_client=refund_client or mock.AsyncMock(),
            orders=order_repository,
            journeys=journey_repository,
            smtp_client=smtp_client,
            environment=environment,
        )

        return handler, context
