import uuid

import pytest

from snowfall.adapter import places
from snowfall.junction.client_api import trips

# todo: would be nice with some "well-known" test data for places etc. in a package.
_PLACES_CLIENT = places.DictClient([{"id": "b212f375-5abf-4864-8ff8-b0b5bdf3e08a"}])


async def _trip_search_request() -> trips.TripSearchRequest:
    return trips.TripSearchRequest(
        origin=await _PLACES_CLIENT.get(
            uuid.UUID("b212f375-5abf-4864-8ff8-b0b5bdf3e08a"),
        ),
        destination=await _PLACES_CLIENT.get(
            uuid.UUID("b212f375-5abf-4864-8ff8-b0b5bdf3e08a"),
        ),
    )


@pytest.mark.asyncio
async def test_trip_search_can_be_saved(
    trip_search_repository: trips.TripSearchRepository,
) -> None:
    await trip_search_repository.create(await _trip_search_request())


@pytest.mark.asyncio
async def test_trip_search_can_be_retrieved(
    trip_search_repository: trips.TripSearchRepository,
) -> None:
    trip_search_created = await trip_search_repository.create(
        await _trip_search_request(),
    )
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
