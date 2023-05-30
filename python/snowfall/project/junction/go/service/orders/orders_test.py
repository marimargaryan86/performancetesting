import more_itertools
import pytest

from snowfall.project.junction.go.service.orders import orders
from snowfall.project.junction.go.service.orders.v1alpha import models_pb2


@pytest.fixture()
async def bookings_cancellation(
    bookings_cancellation_repository: orders.BookingsCancellationsRepository,
    order: models_pb2.Order,
) -> models_pb2.BookingsCancellation:
    ticket_ids = iter(["12345", "56789"])
    return await bookings_cancellation_repository.insert(
        models_pb2.BookingsCancellation(
            booking_cancellations=[
                models_pb2.BookingCancellation(
                    booking_id=booking.id,
                    ticket_id=next(ticket_ids),
                    status=models_pb2.BookingCancellation.STATUS_PENDING,
                )
                for booking in order.bookings
            ],
            status=models_pb2.BookingsCancellation.STATUS_PENDING,
        ),
    )


class TestJourneys(object):
    async def test_journey_is_retrievable_by_id(
        self,
        journey_repository: orders.JourneyRepository,
        order: models_pb2.Order,
    ) -> None:
        journey = await journey_repository.find_by_id(order.journey_id)
        assert journey
        assert journey.id == order.journey_id

    async def test_journey_is_retrievable_by_ids(
        self,
        journey_repository: orders.JourneyRepository,
        order: models_pb2.Order,
    ) -> None:
        journeys_result = await journey_repository.find([order.journey_id], "")
        journeys = [journey async for journey in journeys_result]

        assert len(journeys) == 1
        assert more_itertools.first(journeys).id == order.journey_id


class TestOrders(object):
    async def test_order_is_retrievable_by_id(
        self,
        order_repository: orders.OrderRepository,
        order: models_pb2.Order,
    ) -> None:
        order_resource = await order_repository.find_by_id(order.id)
        assert order_resource
        assert order_resource.id == order.id


class TestBookings(object):
    async def test_booking_can_be_retrieved(
        self,
        booking_repository: orders.BookingRepository,
        order: models_pb2.Order,
    ) -> None:
        booking_id = more_itertools.first(order.bookings).id
        booking = await booking_repository.find_by_id(booking_id)
        assert booking
        assert booking_id == booking.id


class TestBookingDetails(object):
    async def test_booking_details_can_be_retrieved(
        self,
        booking_repository: orders.BookingRepository,
        booking_details_repository: orders.BookingDetailsRepository,
        order: models_pb2.Order,
    ) -> None:
        booking_id = more_itertools.first(order.bookings).id
        booking = await booking_repository.find_by_id(booking_id)
        assert booking
        detail_id = more_itertools.first(booking.trip_option.details).id
        detail = await booking_details_repository.find_by_id(detail_id)
        assert detail
        assert detail_id == detail.id
        assert booking_id == detail.booking_id

    async def test_booking_details_can_be_retrieved_by_ids(
        self,
        booking_repository: orders.BookingRepository,
        booking_details_repository: orders.BookingDetailsRepository,
        order: models_pb2.Order,
    ) -> None:
        booking_id = more_itertools.first(order.bookings).id
        booking = await booking_repository.find_by_id(booking_id)
        assert booking
        detail_ids = [detail.id for detail in booking.trip_option.details]
        details = await booking_details_repository.find(detail_ids, "")
        assert len([detail async for detail in details]) == 2

    async def test_booking_details_can_be_retrieved_by_booking(
        self,
        booking_repository: orders.BookingRepository,
        booking_details_repository: orders.BookingDetailsRepository,
        order: models_pb2.Order,
    ) -> None:
        booking_id = more_itertools.first(order.bookings).id
        details = await booking_details_repository.find_by_booking_id(booking_id, "")
        assert len([detail async for detail in details]) == 2


class TestBookingsCancellations(object):
    async def test_cancellation_is_retrievable_by_id(
        self,
        bookings_cancellation_repository: orders.BookingsCancellationsRepository,
        bookings_cancellation: models_pb2.BookingsCancellation,
    ) -> None:
        retrieved = await bookings_cancellation_repository.find_by_id(
            bookings_cancellation.id,
        )
        assert retrieved
        assert retrieved.id == bookings_cancellation.id
        assert retrieved.status == bookings_cancellation.status
        assert retrieved.created_at.seconds == bookings_cancellation.created_at.seconds

    async def test_cancellation_is_retrievable_by_ticket_id(
        self,
        bookings_cancellation_repository: orders.BookingsCancellationsRepository,
        bookings_cancellation: models_pb2.BookingsCancellation,
    ) -> None:
        ticket_id = more_itertools.first(
            bookings_cancellation.booking_cancellations,
        ).ticket_id

        retrieved = await bookings_cancellation_repository.find_by_ticket_id(ticket_id)

        assert retrieved
        assert retrieved.id == bookings_cancellation.id
        assert retrieved.status == bookings_cancellation.status
        for retrieved_bc, expected_bc in list(  # noqa: WPS352
            zip(
                retrieved.booking_cancellations,
                bookings_cancellation.booking_cancellations,
                strict=True,
            ),
        ):
            assert retrieved_bc == expected_bc

    async def test_can_update_cancellation_status(
        self,
        bookings_cancellation_repository: orders.BookingsCancellationsRepository,
        bookings_cancellation: models_pb2.BookingsCancellation,
    ) -> None:
        bookings_cancellation.status = models_pb2.BookingsCancellation.STATUS_COMPLETED

        update_success = await bookings_cancellation_repository.update(
            bookings_cancellation,
        )

        updated = await bookings_cancellation_repository.find_by_id(
            bookings_cancellation.id,
        )

        assert update_success
        assert updated
        assert updated.id == bookings_cancellation.id
        assert updated.status == bookings_cancellation.status
