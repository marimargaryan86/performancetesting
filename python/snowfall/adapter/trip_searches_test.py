import uuid

import pytest

from snowfall.adapter import trip_searches


@pytest.mark.asyncio
async def test_trip_search_can_be_saved(
    trip_searches_client: trip_searches.Client,
    trip_search_request: trip_searches.TripSearchRequest,
) -> None:
    await trip_searches_client.create(trip_search_request)


@pytest.mark.asyncio
async def test_trip_search_can_be_retrieved(
    trip_searches_client: trip_searches.Client,
    trip_search_request: trip_searches.TripSearchRequest,
) -> None:
    trip_search_created = await trip_searches_client.create(trip_search_request)
    trip_search = await trip_searches_client.get(trip_search_created.identifier)
    assert trip_search == trip_search_created


@pytest.mark.asyncio
async def test_missing_trip_search_throws_error(
    trip_searches_client: trip_searches.Client,
) -> None:
    with pytest.raises(trip_searches.NotFoundError):
        await trip_searches_client.get(uuid.uuid4())
