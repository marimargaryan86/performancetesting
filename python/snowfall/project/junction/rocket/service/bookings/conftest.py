import pytest
from motor import motor_asyncio

from snowfall.project.junction.rocket.service.bookings import repository


@pytest.fixture()
async def booking_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> repository.BookingRepository:
    return repository.BookingRepository(
        collection=mongo_client.test.bookings,
    )


@pytest.fixture()
async def booking_cancellation_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> repository.BookingCancellationRepository:
    return repository.BookingCancellationRepository(
        collection=mongo_client.test.cancellations,
    )
