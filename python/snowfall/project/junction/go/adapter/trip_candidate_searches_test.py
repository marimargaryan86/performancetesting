import pytest

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, trip_candidate_searches


async def test_trip_candidate_search_can_be_saved(
    trip_candidate_searches_client: trip_candidate_searches.Client,
    trip_candidate_search_request: trip_candidate_searches.TripCandidateSearchRequest,
) -> None:
    await trip_candidate_searches_client.create(trip_candidate_search_request)


async def test_trip_candidate_search_can_be_retrieved(
    trip_candidate_searches_client: trip_candidate_searches.Client,
    trip_candidate_search_request: trip_candidate_searches.TripCandidateSearchRequest,
) -> None:
    trip_candidate_search_created = await trip_candidate_searches_client.create(
        trip_candidate_search_request,
    )
    trip_candidate_search = await trip_candidate_searches_client.get(
        trip_candidate_search_created.id,
    )
    assert trip_candidate_search == trip_candidate_search_created


async def test_missing_trip_search_throws_error(
    trip_searches_client: trip_candidate_searches.Client,
) -> None:
    with pytest.raises(errors.NotFoundError):
        await trip_searches_client.get(fixtures.NOT_FOUND)
