import uuid

import pytest

from snowfall.adapter import places
from snowfall.junction.client_api import trips

_TEST_TRIP = trips.TripSearchRequest(
    origin=places.Place(identifier=uuid.uuid4(), name="foobar"),
    destination=places.Place(identifier=uuid.uuid4(), name="bazqux"),
)


@pytest.mark.asyncio
async def test_trip_search_can_be_saved(
    trip_search_repository: trips.TripSearchRepository,
) -> None:
    await trip_search_repository.create(_TEST_TRIP)


@pytest.mark.asyncio
async def test_trip_search_can_be_retrieved(
    trip_search_repository: trips.TripSearchRepository,
) -> None:
    trip_search_created = await trip_search_repository.create(_TEST_TRIP)
    trip_search = await trip_search_repository.get(
        trip_search_created.identifier,
    )
    assert trip_search == trip_search_created


@pytest.mark.asyncio
async def test_missing_trip_search_throws_error(
    trip_search_repository: trips.TripSearchRepository,
) -> None:
    with pytest.raises(trips.NotFoundError):
        await trip_search_repository.get(uuid.uuid4())
