import pytest

from snowfall import fixtures
from snowfall.project.junction.adapter import trip_searches


async def test_trip_search_can_be_saved(
    trip_searches_client: trip_searches.Client,
    trip_search_request: trip_searches.TripSearchRequest,
) -> None:
    await trip_searches_client.create(trip_search_request)


async def test_trip_search_can_be_retrieved(
    trip_searches_client: trip_searches.Client,
    trip_search_request: trip_searches.TripSearchRequest,
) -> None:
    trip_search_created = await trip_searches_client.create(trip_search_request)
    trip_search = await trip_searches_client.get(trip_search_created.id)
    assert trip_search == trip_search_created


async def test_missing_trip_search_throws_error(
    trip_searches_client: trip_searches.Client,
) -> None:
    with pytest.raises(trip_searches.NotFoundError):
        await trip_searches_client.get(fixtures.NOT_FOUND)
