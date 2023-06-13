import pathlib
from collections.abc import AsyncIterator

import pytest

from snowfall.project.junction.provider import bookings
from snowfall.project.junction.provider.v1alpha import bookings_pb2
from snowfall.stdlib.persistence import filesystem


class _MockTransformer(object):
    async def raw_to_booking(self, raw: bytes) -> bookings_pb2.Booking:
        return bookings_pb2.Booking(
            id=raw.decode(),
        )


@pytest.fixture()
async def storage() -> AsyncIterator[filesystem.Storage]:
    async with filesystem.Storage.from_dsn("memory://") as storage_obj:
        yield storage_obj


@pytest.fixture()
def implementation(storage: filesystem.Storage) -> bookings.Implementation:
    return bookings.Implementation(
        storage=storage,
        transformer=_MockTransformer().raw_to_booking,
    )


class TestImplementation(object):
    async def test_booking_can_be_retrieved(
        self,
        implementation: bookings.Implementation,
        storage: filesystem.Storage,
    ) -> None:
        identifier = "foo"
        await storage.put(pathlib.Path(identifier), identifier.encode())
        booking = await implementation.get(identifier=identifier)

        assert booking.id == identifier

    async def test_missing_booking_fails(
        self,
        implementation: bookings.Implementation,
    ) -> None:
        with pytest.raises(bookings.NotFoundError):
            await implementation.get(identifier="foo")
