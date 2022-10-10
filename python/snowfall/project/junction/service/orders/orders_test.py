import more_itertools
import pytest

from snowfall.project.junction.service.orders import orders
from snowfall.project.junction.service.orders.v1alpha import models_pb2


@pytest.fixture
async def order(
    journey_repository: orders.JourneyRepository,
    order_repository: orders.OrderRepository,
) -> models_pb2.Order:
    journey = await journey_repository.create(
        contact_details=models_pb2.ContactDetails(),
    )
    return await order_repository.create_from_options(
        journey_id=journey.id,
        passengers=[
            models_pb2.Passenger(),
        ],
        options=[
            models_pb2.TripOption(
                details=[
                    models_pb2.TripOptionDetails(),
                    models_pb2.TripOptionDetails(),
                ],
            ),
            models_pb2.TripOption(
                details=[
                    models_pb2.TripOptionDetails(),
                ],
            ),
        ],
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

    async def test_booking_can_be_updated(
        self,
        journey_repository: orders.JourneyRepository,
        booking_repository: orders.BookingRepository,
        order: models_pb2.Order,
    ) -> None:
        original_booking = more_itertools.first(order.bookings)
        original_booking.status = models_pb2.Booking.STATUS_CONFIRMED
        await booking_repository.update(original_booking)
        updated_booking = await booking_repository.find_by_id(original_booking.id)
        assert updated_booking
        assert updated_booking.status == models_pb2.Booking.STATUS_CONFIRMED


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
