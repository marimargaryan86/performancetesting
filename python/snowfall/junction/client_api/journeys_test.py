import uuid

import pytest

from snowfall.junction.client_api import journeys, places

_TEST_JOURNEY = journeys.JourneySearchRequest(
    origin=places.Place(identifier=uuid.uuid4()),
    destination=places.Place(identifier=uuid.uuid4()),
)


@pytest.mark.asyncio
async def test_journey_search_can_be_saved(
    journey_search_repository: journeys.JourneySearchRepository,
) -> None:
    await journey_search_repository.create(_TEST_JOURNEY)


@pytest.mark.asyncio
async def test_journey_search_can_be_retrieved(
    journey_search_repository: journeys.JourneySearchRepository,
) -> None:
    journey_search_created = await journey_search_repository.create(_TEST_JOURNEY)
    journey_search = await journey_search_repository.get(
        journey_search_created.identifier,
    )
    assert journey_search == journey_search_created


@pytest.mark.asyncio
async def test_missing_journey_search_throws_error(
    journey_search_repository: journeys.JourneySearchRepository,
) -> None:
    with pytest.raises(journeys.NotFoundError):
        await journey_search_repository.get(uuid.uuid4())
