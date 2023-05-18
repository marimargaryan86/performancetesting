import pytest
from motor import motor_asyncio

from snowfall.project.junction.go.adapter import passenger_name_records
from snowfall.project.junction.go.service.orders import orders


@pytest.fixture()
def pnr_client() -> passenger_name_records.Client:
    return passenger_name_records.DictClient([])


@pytest.fixture()
def journey_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
    pnr_client: passenger_name_records.Client,
) -> orders.JourneyRepository:
    return orders.JourneyRepository(
        collection=mongo_client.test.journeys,
        passenger_name_records=pnr_client,
    )


@pytest.fixture()
def order_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> orders.OrderRepository:
    return orders.OrderRepository(
        collection=mongo_client.test.journeys,
    )


@pytest.fixture()
def booking_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> orders.BookingRepository:
    return orders.BookingRepository(
        collection=mongo_client.test.journeys,
    )


@pytest.fixture()
def booking_details_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> orders.BookingDetailsRepository:
    return orders.BookingDetailsRepository(
        collection=mongo_client.test.journeys,
    )


@pytest.fixture()
def bookings_cancellation_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> orders.BookingsCancellationsRepository:
    return orders.BookingsCancellationsRepository(
        collection=mongo_client.test.order_cancellations,
    )
